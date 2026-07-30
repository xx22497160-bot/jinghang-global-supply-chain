#!/usr/bin/env python3
"""Read-only SEO monitoring and report generation for jinghangsc.com.

The script intentionally does not edit public HTML, submit sitemaps, call an
indexing API, publish content, commit changes, deploy, or contact third parties.
It uses only Python's standard library so it can run locally or in GitHub
Actions without installing dependencies.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import html
import json
import os
import re
import socket
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo


CANONICAL_ORIGIN = "https://jinghangsc.com"
EXPECTED_CANONICAL_URL_COUNT = 15
CROSS_PROJECT_MARKER = "Tools" + "168"
CHINA_TZ = ZoneInfo("Asia/Shanghai")
USER_AGENT = "JinghangSEOHealthMonitor/1.0 (+https://jinghangsc.com/)"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_ROOT = PROJECT_ROOT / "seo" / "reports"
DEFAULT_STATE_FILE = PROJECT_ROOT / "seo" / "state" / "daily-latest.json"


@dataclass
class Issue:
    severity: str
    code: str
    message: str
    url: str = ""

    @property
    def fingerprint(self) -> str:
        raw = "|".join((self.severity, self.code, self.url, self.message))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


@dataclass
class PageRecord:
    url: str
    local_file: str
    title: str = ""
    description: str = ""
    h1: str = ""
    canonical: str = ""
    robots: str = ""
    html_lang: str = ""
    word_count: int = 0
    internal_link_count: int = 0
    json_ld_blocks: int = 0
    image_count: int = 0
    missing_alt_count: int = 0
    live_status: str = "not checked"
    live_final_url: str = "not checked"


@dataclass
class AuditResult:
    site_dir: str
    sitemap_url_count: int
    pages: list[PageRecord] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)
    search_console_status: str = "未连接 (Not connected)"
    bing_status: str = "未连接 (Not connected)"


class StaticHTMLParser(HTMLParser):
    """Collect the SEO fields needed by the safe monitor."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.h1_parts: list[list[str]] = []
        self.description = ""
        self.canonical = ""
        self.robots = ""
        self.html_lang = ""
        self.hrefs: list[str] = []
        self.srcs: list[str] = []
        self.form_actions: list[tuple[str, str]] = []
        self.json_ld: list[str] = []
        self.og: dict[str, str] = {}
        self.image_count = 0
        self.missing_alt_count = 0
        self.visible_parts: list[str] = []
        self._in_title = False
        self._h1_depth = 0
        self._in_json_ld = False
        self._json_parts: list[str] = []
        self._excluded_depth = 0
        self._in_body = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        lowered = tag.lower()
        if lowered == "html":
            self.html_lang = values.get("lang", "")
        elif lowered == "body":
            self._in_body = True
        elif lowered == "title":
            self._in_title = True
        elif lowered == "h1":
            self._h1_depth += 1
            self.h1_parts.append([])
        elif lowered in {"script", "style", "noscript"}:
            self._excluded_depth += 1
        if lowered == "a" and values.get("href"):
            self.hrefs.append(values["href"])
        if values.get("src"):
            self.srcs.append(values["src"])
        if lowered == "form":
            self.form_actions.append(
                (values.get("action", ""), values.get("method", "get").lower())
            )
        if lowered == "meta":
            name = values.get("name", "").lower()
            prop = values.get("property", "").lower()
            content = values.get("content", "")
            if name == "description":
                self.description = content.strip()
            elif name == "robots":
                self.robots = content.strip()
            if prop.startswith("og:"):
                self.og[prop] = content.strip()
        if lowered == "link" and "canonical" in values.get("rel", "").lower().split():
            self.canonical = values.get("href", "").strip()
        if lowered == "img":
            self.image_count += 1
            if "alt" not in values:
                self.missing_alt_count += 1
        if lowered == "script" and values.get("type", "").lower() == "application/ld+json":
            self._in_json_ld = True
            self._json_parts = []

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered == "title":
            self._in_title = False
        elif lowered == "h1" and self._h1_depth:
            self._h1_depth -= 1
        elif lowered in {"script", "style", "noscript"} and self._excluded_depth:
            if lowered == "script" and self._in_json_ld:
                self.json_ld.append("".join(self._json_parts).strip())
                self._in_json_ld = False
                self._json_parts = []
            self._excluded_depth -= 1
        elif lowered == "body":
            self._in_body = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._h1_depth and self.h1_parts:
            self.h1_parts[-1].append(data)
        if self._in_json_ld:
            self._json_parts.append(data)
        if self._in_body and not self._excluded_depth:
            value = clean_text(data)
            if value:
                self.visible_parts.append(value)


class RedirectRecorder(urllib.request.HTTPRedirectHandler):
    def __init__(self, allowed_hosts: set[str]) -> None:
        super().__init__()
        self.chain: list[str] = []
        self.allowed_hosts = allowed_hosts

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> urllib.request.Request | None:
        self.chain.append(newurl)
        if (urllib.parse.urlsplit(newurl).hostname or "").lower() not in self.allowed_hosts:
            return None
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def clean_text(value: str) -> str:
    return " ".join(value.split())


def normalize_markup_text(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value)
    normalized = clean_text(html.unescape(without_tags))
    return re.sub(r"\s+([.,;:!?])", r"\1", normalized)


def visible_faq_entries(source: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    details_pattern = re.compile(
        r'<details[^>]*class=["\'][^"\']*\bfaq-item\b[^"\']*["\'][^>]*>(.*?)</details>',
        re.S | re.I,
    )
    for details in details_pattern.findall(source):
        summary_match = re.search(r"<summary[^>]*>(.*?)</summary>", details, re.S | re.I)
        answer_match = re.search(
            r'<(?:div|section)[^>]*class=["\'][^"\']*\bfaq-answer\b[^"\']*["\'][^>]*>(.*)</(?:div|section)>',
            details,
            re.S | re.I,
        )
        if summary_match and answer_match:
            entries[normalize_markup_text(summary_match.group(1))] = normalize_markup_text(
                answer_match.group(1)
            )
    return entries


def schema_nodes(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from schema_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from schema_nodes(child)


def schema_faq_entries(payloads: list[str]) -> tuple[list[dict[str, str]], list[str]]:
    faq_sets: list[dict[str, str]] = []
    same_as_values: list[str] = []
    for payload in payloads:
        try:
            structured = json.loads(payload)
        except json.JSONDecodeError:
            continue
        for node in schema_nodes(structured):
            same_as = node.get("sameAs")
            if isinstance(same_as, str):
                same_as_values.append(same_as)
            elif isinstance(same_as, list):
                same_as_values.extend(str(item) for item in same_as)
            if node.get("@type") != "FAQPage":
                continue
            entries: dict[str, str] = {}
            for item in node.get("mainEntity", []):
                if not isinstance(item, dict):
                    continue
                answer = item.get("acceptedAnswer", {})
                if isinstance(answer, dict):
                    entries[normalize_markup_text(str(item.get("name", "")))] = (
                        normalize_markup_text(str(answer.get("text", "")))
                    )
            faq_sets.append(entries)
    return faq_sets, same_as_values


def now_china() -> datetime:
    return datetime.now(CHINA_TZ)


def find_site_dir(explicit: str | None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    env_site = os.environ.get("SEO_SITE_DIR")
    if env_site:
        candidates.append(Path(env_site).expanduser())
    candidates.extend(
        [
            PROJECT_ROOT / "english_website_project" / "site",
            PROJECT_ROOT,
            Path.cwd() / "english_website_project" / "site",
            Path.cwd(),
        ]
    )
    for candidate in candidates:
        resolved = candidate.resolve()
        if (resolved / "index.html").is_file() and (resolved / "sitemap.xml").is_file():
            return resolved
    raise FileNotFoundError(
        "Could not locate the static site. Pass --site-dir or set SEO_SITE_DIR."
    )


def sitemap_urls(site_dir: Path) -> tuple[list[str], list[Issue]]:
    path = site_dir / "sitemap.xml"
    issues: list[Issue] = []
    if not path.exists():
        return [], [Issue("error", "sitemap_missing", "sitemap.xml is missing")]
    try:
        root = ET.fromstring(path.read_text(encoding="utf-8"))
    except (ET.ParseError, UnicodeDecodeError) as exc:
        return [], [Issue("error", "sitemap_invalid", f"sitemap.xml is invalid: {exc}")]
    urls: list[str] = []
    for node in root.findall(".//{*}loc"):
        if node.text and node.text.strip():
            urls.append(node.text.strip())
    if not urls:
        issues.append(Issue("error", "sitemap_empty", "sitemap.xml contains no URL entries"))
    if len(urls) != len(set(urls)):
        issues.append(Issue("warning", "sitemap_duplicates", "sitemap.xml contains duplicate URLs"))
    return urls, issues


def local_file_for_url(site_dir: Path, url: str) -> Path | None:
    path = urllib.parse.urlsplit(url).path
    relative = path.lstrip("/")
    candidates: list[Path]
    if not relative:
        candidates = [site_dir / "index.html"]
    elif path.endswith("/"):
        candidates = [site_dir / relative / "index.html", site_dir / f"{relative.rstrip('/')}.html"]
    else:
        candidates = [
            site_dir / relative,
            site_dir / f"{relative}.html",
            site_dir / relative / "index.html",
        ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def parse_html(path: Path) -> StaticHTMLParser:
    parser = StaticHTMLParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def internal_target_exists(site_dir: Path, source_url: str, href: str) -> bool:
    if href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return True
    parsed = urllib.parse.urlsplit(href)
    if parsed.scheme in {"http", "https"}:
        if parsed.netloc not in {"jinghangsc.com", "www.jinghangsc.com"}:
            return True
        target_url = f"{CANONICAL_ORIGIN}{parsed.path or '/'}"
    elif parsed.scheme or parsed.netloc:
        return True
    elif href.startswith("/"):
        target_url = f"{CANONICAL_ORIGIN}{parsed.path or '/'}"
    else:
        base = urllib.parse.urljoin(source_url, href)
        target_url = f"{CANONICAL_ORIGIN}{urllib.parse.urlsplit(base).path}"
    target_path = urllib.parse.urlsplit(target_url).path
    static_candidate = site_dir / target_path.lstrip("/")
    if static_candidate.is_file():
        return True
    return local_file_for_url(site_dir, target_url) is not None


def audit_local(site_dir: Path) -> AuditResult:
    urls, issues = sitemap_urls(site_dir)
    records: list[PageRecord] = []
    parsed_pages: dict[str, StaticHTMLParser] = {}
    titles: dict[str, list[str]] = {}
    descriptions: dict[str, list[str]] = {}
    canonical_values: dict[str, list[str]] = {}
    if len(urls) != EXPECTED_CANONICAL_URL_COUNT:
        issues.append(
            Issue(
                "error",
                "canonical_url_count",
                f"Expected {EXPECTED_CANONICAL_URL_COUNT} canonical sitemap URLs; found {len(urls)}",
            )
        )

    robots_path = site_dir / "robots.txt"
    if not robots_path.exists():
        issues.append(Issue("error", "robots_missing", "robots.txt is missing"))
    else:
        robots_text = robots_path.read_text(encoding="utf-8")
        expected = f"Sitemap: {CANONICAL_ORIGIN}/sitemap.xml"
        if expected not in robots_text:
            issues.append(
                Issue("error", "robots_sitemap_missing", f"robots.txt must contain {expected}")
            )
        if re.search(r"(?im)^\s*disallow:\s*/\s*$", robots_text):
            issues.append(Issue("error", "robots_blocks_site", "robots.txt blocks the entire site"))

    for url in urls:
        parsed_url = urllib.parse.urlsplit(url)
        if f"{parsed_url.scheme}://{parsed_url.netloc}" != CANONICAL_ORIGIN:
            issues.append(
                Issue("error", "sitemap_noncanonical_host", "Sitemap URL is not on the canonical HTTPS host", url)
            )
        path = local_file_for_url(site_dir, url)
        if path is None:
            issues.append(Issue("error", "sitemap_target_missing", "Sitemap URL has no local page", url))
            continue
        try:
            parser = parse_html(path)
        except (OSError, UnicodeDecodeError) as exc:
            issues.append(Issue("error", "html_unreadable", f"Could not read HTML: {exc}", url))
            continue
        parsed_pages[url] = parser
        source = path.read_text(encoding="utf-8")

        title = clean_text("".join(parser.title_parts))
        h1_values = [clean_text("".join(parts)) for parts in parser.h1_parts]
        h1 = h1_values[0] if h1_values else ""
        record = PageRecord(
            url=url,
            local_file=path.relative_to(site_dir).as_posix(),
            title=title,
            description=parser.description,
            h1=h1,
            canonical=parser.canonical,
            robots=parser.robots,
            html_lang=parser.html_lang,
            word_count=len(re.findall(r"\b[\w'-]+\b", " ".join(parser.visible_parts))),
            internal_link_count=sum(
                1
                for href in parser.hrefs
                if not urllib.parse.urlsplit(href).netloc
                or urllib.parse.urlsplit(href).netloc in {"jinghangsc.com", "www.jinghangsc.com"}
            ),
            json_ld_blocks=len(parser.json_ld),
            image_count=parser.image_count,
            missing_alt_count=parser.missing_alt_count,
        )
        records.append(record)

        if not title:
            issues.append(Issue("error", "title_missing", "Page title is missing", url))
        else:
            titles.setdefault(title, []).append(url)
        if not parser.description:
            issues.append(Issue("error", "description_missing", "Meta description is missing", url))
        else:
            descriptions.setdefault(parser.description, []).append(url)
        if len(h1_values) != 1 or not h1:
            issues.append(
                Issue("error", "h1_invalid", f"Expected one non-empty H1; found {len(h1_values)}", url)
            )
        if parser.canonical != url:
            issues.append(
                Issue(
                    "error",
                    "canonical_mismatch",
                    f"Canonical is {parser.canonical or 'missing'}; expected {url}",
                    url,
                )
            )
        elif parser.canonical:
            canonical_values.setdefault(parser.canonical, []).append(url)
        if "noindex" in parser.robots.lower():
            issues.append(Issue("error", "unexpected_noindex", "Indexable sitemap URL contains noindex", url))
        if parser.html_lang.lower() != "en":
            issues.append(Issue("warning", "html_lang", "Expected html lang=en", url))
        for block_number, payload in enumerate(parser.json_ld, start=1):
            try:
                json.loads(payload)
            except json.JSONDecodeError as exc:
                issues.append(
                    Issue(
                        "error",
                        "jsonld_invalid",
                        f"JSON-LD block {block_number} is invalid: {exc}",
                        url,
                    )
                )
        if not parser.json_ld:
            issues.append(Issue("warning", "jsonld_missing", "Page contains no JSON-LD", url))
        faq_sets, same_as_values = schema_faq_entries(parser.json_ld)
        if len(faq_sets) > 1:
            issues.append(
                Issue(
                    "error",
                    "faq_schema_duplicate",
                    f"Expected no more than one FAQPage node; found {len(faq_sets)}",
                    url,
                )
            )
        visible_faq = visible_faq_entries(source)
        if faq_sets or visible_faq:
            schema_faq = faq_sets[0] if faq_sets else {}
            if visible_faq != schema_faq:
                missing_schema = sorted(set(visible_faq) - set(schema_faq))
                missing_visible = sorted(set(schema_faq) - set(visible_faq))
                differing = sorted(
                    question
                    for question in set(visible_faq) & set(schema_faq)
                    if visible_faq[question] != schema_faq[question]
                )
                detail: list[str] = []
                if missing_schema:
                    detail.append(f"{len(missing_schema)} visible question(s) missing from schema")
                if missing_visible:
                    detail.append(f"{len(missing_visible)} schema question(s) missing from visible content")
                if differing:
                    detail.append(f"{len(differing)} answer(s) differ")
                issues.append(
                    Issue(
                        "error",
                        "faq_visible_schema_mismatch",
                        "; ".join(detail) or "Visible and structured FAQ content differ",
                        url,
                    )
                )
        if url == f"{CANONICAL_ORIGIN}/faq" and len(visible_faq) != 27:
            issues.append(
                Issue(
                    "error",
                    "faq_count",
                    f"Expected 27 visible FAQ entries; found {len(visible_faq)}",
                    url,
                )
            )
        if same_as_values:
            issues.append(
                Issue(
                    "error",
                    "unverified_same_as",
                    "Structured data contains sameAs without a verified social profile",
                    url,
                )
            )
        if parser.missing_alt_count:
            issues.append(
                Issue(
                    "warning",
                    "image_alt_missing",
                    f"{parser.missing_alt_count} image(s) have no alt attribute",
                    url,
                )
            )
        required_og = {"og:title", "og:description", "og:url", "og:image"}
        missing_og = sorted(required_og - set(parser.og))
        if missing_og:
            issues.append(
                Issue("warning", "open_graph_missing", f"Missing Open Graph fields: {', '.join(missing_og)}", url)
            )
        for href in parser.hrefs:
            if not internal_target_exists(site_dir, url, href):
                issues.append(
                    Issue("error", "internal_link_broken", f"Internal link target not found: {href}", url)
                )
        for src in parser.srcs:
            parsed_src = urllib.parse.urlsplit(src)
            if parsed_src.scheme in {"http", "https", "data"} or parsed_src.netloc:
                continue
            source_path = site_dir / parsed_src.path.lstrip("/")
            if not source_path.is_file():
                issues.append(
                    Issue("error", "asset_missing", f"Referenced asset not found: {src}", url)
                )

    for label, values, code in (
        ("title", titles, "duplicate_title"),
        ("meta description", descriptions, "duplicate_description"),
        ("canonical", canonical_values, "duplicate_canonical"),
    ):
        for value, value_urls in values.items():
            if len(value_urls) > 1:
                issues.append(
                    Issue(
                        "error",
                        code,
                        f"Duplicate {label} across {len(value_urls)} pages: {value}",
                        ", ".join(value_urls),
                    )
                )

    for html_path in site_dir.rglob("*.html"):
        source = html_path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"https?://(?:localhost|127\.0\.0\.1|[^/\"']+\.pages\.dev)", source, re.I):
            issues.append(
                Issue(
                    "error",
                    "test_domain_reference",
                    f"Production HTML references a test or preview host in {html_path.relative_to(site_dir)}",
                )
            )

    contact_url = f"{CANONICAL_ORIGIN}/contact"
    contact_parser = parsed_pages.get(contact_url)
    if contact_parser is None:
        issues.append(Issue("error", "contact_page_missing", "Contact page is missing from the sitemap"))
    else:
        if contact_parser.form_actions != [("/api/contact", "post")]:
            issues.append(
                Issue(
                    "error",
                    "contact_form_action",
                    f"Expected one POST form to /api/contact; found {contact_parser.form_actions}",
                    contact_url,
                )
            )
        if "/contact.js" not in contact_parser.srcs:
            issues.append(
                Issue("error", "contact_script_missing", "Contact page does not load /contact.js", contact_url)
            )
    for function_path in (
        site_dir / "functions" / "api" / "contact.js",
        site_dir / "functions" / "api" / "contact-config.js",
    ):
        if not function_path.is_file():
            issues.append(
                Issue(
                    "error",
                    "contact_function_missing",
                    f"Secure form function is missing: {function_path.relative_to(site_dir)}",
                    contact_url,
                )
            )

    runtime_extensions = {".html", ".js", ".css", ".xml", ".txt", ".svg"}
    for runtime_path in site_dir.rglob("*"):
        if not runtime_path.is_file() or runtime_path.suffix.lower() not in runtime_extensions:
            continue
        relative_parts = runtime_path.relative_to(site_dir).parts
        if any(part in {".git", ".github", "seo"} for part in relative_parts):
            continue
        runtime_source = runtime_path.read_text(encoding="utf-8", errors="replace")
        relative_name = runtime_path.relative_to(site_dir).as_posix()
        if re.search(rf"\b{re.escape(CROSS_PROJECT_MARKER)}\b", runtime_source, re.I):
            issues.append(
                Issue(
                    "error",
                    "cross_project_reference",
                    f"Jinghang runtime source contains an unrelated project-brand reference: {relative_name}",
                )
            )
        if runtime_path.suffix.lower() == ".html":
            if re.search(r"(?:linkedin\.com|\bLinkedIn\b)", runtime_source, re.I):
                issues.append(
                    Issue(
                        "error",
                        "unverified_linkedin",
                        f"Public HTML contains an unverified LinkedIn reference: {relative_name}",
                    )
                )
            if re.search(r"\bWeChat\b", runtime_source, re.I):
                issues.append(
                    Issue(
                        "error",
                        "unverified_wechat",
                        f"Public HTML contains an unverified WeChat reference: {relative_name}",
                    )
                )

    headers_path = site_dir / "_headers"
    if not headers_path.is_file():
        issues.append(Issue("error", "headers_missing", "_headers is missing"))
    else:
        header_source = headers_path.read_text(encoding="utf-8")
        configured_hashes = set(re.findall(r"sha256-[A-Za-z0-9+/=]+", header_source))
        current_hashes: set[str] = set()
        inline_script_pattern = re.compile(
            rb"<script(?![^>]*\bsrc\s*=)[^>]*>(.*?)</script>",
            re.S | re.I,
        )
        for html_path in site_dir.rglob("*.html"):
            for payload in inline_script_pattern.findall(html_path.read_bytes()):
                digest = base64.b64encode(hashlib.sha256(payload).digest()).decode("ascii")
                current_hashes.add(f"sha256-{digest}")
        missing_hashes = sorted(current_hashes - configured_hashes)
        stale_hashes = sorted(configured_hashes - current_hashes)
        if missing_hashes:
            issues.append(
                Issue(
                    "error",
                    "csp_hash_missing",
                    f"_headers is missing {len(missing_hashes)} current inline-script hash(es)",
                )
            )
        if stale_hashes:
            issues.append(
                Issue(
                    "error",
                    "csp_hash_stale",
                    f"_headers contains {len(stale_hashes)} stale inline-script hash(es)",
                )
            )
        if "'unsafe-inline'" in header_source:
            issues.append(
                Issue("error", "csp_unsafe_inline", "CSP script policy contains unsafe-inline")
            )

    return AuditResult(
        site_dir=str(site_dir),
        sitemap_url_count=len(urls),
        pages=records,
        issues=deduplicate_issues(issues),
    )


def deduplicate_issues(issues: Iterable[Issue]) -> list[Issue]:
    unique: dict[str, Issue] = {}
    for issue in issues:
        unique[issue.fingerprint] = issue
    return sorted(unique.values(), key=lambda item: (item.severity, item.code, item.url, item.message))


def fetch_url(url: str, timeout: float = 20.0) -> tuple[int | None, str, list[str], dict[str, str], str]:
    redirect_handler = RedirectRecorder({"jinghangsc.com", "www.jinghangsc.com"})
    opener = urllib.request.build_opener(redirect_handler)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*;q=0.8"})
    try:
        with opener.open(request, timeout=timeout) as response:
            body = response.read(2_000_000).decode("utf-8", errors="replace")
            headers = {key.lower(): value for key, value in response.headers.items()}
            return response.status, response.geturl(), redirect_handler.chain, headers, body
    except urllib.error.HTTPError as exc:
        body = exc.read(2_000_000).decode("utf-8", errors="replace")
        headers = {key.lower(): value for key, value in exc.headers.items()}
        return exc.code, exc.geturl(), redirect_handler.chain, headers, body
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return None, url, redirect_handler.chain, {}, f"{type(exc).__name__}: {exc}"


def ssl_expiry(hostname: str, timeout: float = 10.0) -> tuple[datetime | None, str]:
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, 443), timeout=timeout) as raw:
            with context.wrap_socket(raw, server_hostname=hostname) as secured:
                certificate = secured.getpeercert()
    except (OSError, ssl.SSLError) as exc:
        return None, f"{type(exc).__name__}: {exc}"
    expires = certificate.get("notAfter")
    if not expires:
        return None, "Certificate did not expose notAfter"
    try:
        parsed = datetime.strptime(expires, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        return None, f"Could not parse certificate expiry: {exc}"
    return parsed, ""


def add_live_checks(audit: AuditResult, base_url: str) -> None:
    canonical_origin = base_url.rstrip("/")
    host = urllib.parse.urlsplit(canonical_origin).hostname or "jinghangsc.com"
    expiry, ssl_error = ssl_expiry(host)
    if ssl_error:
        audit.issues.append(Issue("error", "ssl_check_failed", ssl_error, canonical_origin))
    elif expiry:
        remaining_days = (expiry - datetime.now(timezone.utc)).days
        if remaining_days < 14:
            audit.issues.append(
                Issue("error", "ssl_expiring", f"TLS certificate expires in {remaining_days} day(s)", canonical_origin)
            )

    variants = [
        "http://jinghangsc.com/",
        "https://jinghangsc.com/",
        "http://www.jinghangsc.com/",
        "https://www.jinghangsc.com/",
    ]
    for variant in variants:
        status, final_url, chain, _headers, _body = fetch_url(variant)
        if status != 200:
            audit.issues.append(
                Issue("error", "canonical_variant_status", f"Expected final status 200; received {status}", variant)
            )
        if final_url.rstrip("/") != canonical_origin:
            audit.issues.append(
                Issue(
                    "error",
                    "canonical_variant_target",
                    f"Final URL is {final_url}; expected {canonical_origin}/",
                    variant,
                )
            )
        if len(chain) > 1:
            audit.issues.append(
                Issue("warning", "redirect_chain", f"Redirect chain contains {len(chain)} hops", variant)
            )

    live_by_url: dict[str, PageRecord] = {record.url: record for record in audit.pages}
    for record in audit.pages:
        status, final_url, chain, _headers, body = fetch_url(record.url)
        record.live_status = str(status) if status is not None else "request failed"
        record.live_final_url = final_url
        if status != 200:
            audit.issues.append(
                Issue("error", "live_page_status", f"Expected 200; received {status}", record.url)
            )
        if final_url != record.url:
            audit.issues.append(
                Issue("warning", "live_page_redirect", f"Sitemap URL resolves to {final_url}", record.url)
            )
        if len(chain) > 1:
            audit.issues.append(
                Issue("warning", "redirect_chain", f"Redirect chain contains {len(chain)} hops", record.url)
            )
        if re.search(r"https?://(?:localhost|127\.0\.0\.1|[^/\"']+\.pages\.dev)", body, re.I):
            audit.issues.append(
                Issue("error", "live_test_domain_reference", "Live HTML references a test or preview host", record.url)
            )

    for special in (f"{canonical_origin}/robots.txt", f"{canonical_origin}/sitemap.xml"):
        status, _final_url, _chain, _headers, _body = fetch_url(special)
        if status != 200:
            audit.issues.append(
                Issue("error", "live_technical_file_status", f"Expected 200; received {status}", special)
            )

    if f"{canonical_origin}/contact" not in live_by_url:
        audit.issues.append(
            Issue("error", "contact_not_in_sitemap", "Contact page is not represented in the sitemap")
        )
    audit.issues = deduplicate_issues(audit.issues)


def optional_data_status(explicit: str | None, default_path: Path, label: str) -> tuple[str, list[dict[str, Any]]]:
    path_value = explicit or os.environ.get(f"SEO_{label.upper()}_EXPORT")
    path = Path(path_value).expanduser() if path_value else default_path
    if not path.exists():
        return "未连接 (Not connected)", []
    try:
        if path.suffix.lower() == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                rows = payload.get("rows", [])
            else:
                rows = payload
            if not isinstance(rows, list):
                raise ValueError("JSON export must be a list or an object with a rows list")
            return f"Connected export: {path.name} ({len(rows)} rows)", [
                row for row in rows if isinstance(row, dict)
            ]
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        return f"Connected export: {path.name} ({len(rows)} rows)", rows
    except (OSError, ValueError, json.JSONDecodeError, csv.Error) as exc:
        return f"读取失败 (Could not read export: {exc})", []


def issue_lines(issues: list[Issue]) -> list[str]:
    if not issues:
        return ["- None."]
    return [
        f"- **{issue.severity.upper()} · {issue.code}**"
        + (f" — `{issue.url}`" if issue.url else "")
        + f": {issue.message}"
        for issue in issues
    ]


def load_previous_state(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    issues = payload.get("issues", []) if isinstance(payload, dict) else []
    return {
        str(item.get("fingerprint")): item
        for item in issues
        if isinstance(item, dict) and item.get("fingerprint")
    }


def save_state(path: Path, audit: AuditResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": now_china().isoformat(),
        "issues": [
            {
                **asdict(issue),
                "fingerprint": issue.fingerprint,
            }
            for issue in audit.issues
        ],
        "sitemap_url_count": audit.sitemap_url_count,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_report(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def daily_report(
    audit: AuditResult,
    report_path: Path,
    state_path: Path,
    live_checked: bool,
) -> None:
    previous = load_previous_state(state_path)
    current = {issue.fingerprint: issue for issue in audit.issues}
    new_issues = [issue for fingerprint, issue in current.items() if fingerprint not in previous]
    restored = [value for fingerprint, value in previous.items() if fingerprint not in current]
    errors = [issue for issue in audit.issues if issue.severity == "error"]
    warnings = [issue for issue in audit.issues if issue.severity == "warning"]
    status = "ATTENTION REQUIRED" if errors else ("WARNING" if warnings else "NORMAL")
    generated = now_china()

    lines = [
        f"# Daily SEO Health Report — {generated.date().isoformat()}",
        "",
        f"- **Status:** {status}",
        f"- **Generated:** {generated.strftime('%Y-%m-%d %H:%M:%S %Z')} "
        f"({generated.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')})",
        f"- **Mode:** {'Local and live read-only checks' if live_checked else 'Local read-only checks'}",
        f"- **Sitemap URLs:** {audit.sitemap_url_count}",
        f"- **Google Search Console:** {audit.search_console_status}",
        f"- **Bing Webmaster Tools:** {audit.bing_status}",
        "",
        "Search-platform data is never inferred. `未连接` means no readable export or authorized API connection was available; it does not mean zero impressions, clicks, indexed pages, or enquiries.",
        "",
        "## New Issues",
        "",
        *issue_lines(new_issues),
        "",
        "## Restored Issues",
        "",
    ]
    if restored:
        lines.extend(
            f"- **{item.get('severity', '').upper()} · {item.get('code', '')}**"
            + (f" — `{item.get('url')}`" if item.get("url") else "")
            + f": {item.get('message', '')}"
            for item in restored
        )
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Current Technical Findings",
            "",
            *issue_lines(audit.issues),
            "",
            "## Data Changes",
            "",
            "- Search performance change: unavailable while Search Console and Bing data are not connected.",
            "- Enquiry-event change: unavailable while an approved analytics implementation is not connected.",
            "- No sitemap submission or indexing request was made by this monitor.",
            "",
            "## Manual Action",
            "",
        ]
    )
    if audit.issues:
        lines.append("- Review the issues above. This task did not edit page copy, publish content, deploy, submit a sitemap, or contact any third party.")
    else:
        lines.append("- No technical action is required from this run.")
    write_report(report_path, "\n".join(lines))
    save_state(state_path, audit)


def normalize_number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(str(value).replace("%", "").replace(",", "").strip())
    except ValueError:
        return None


def weekly_candidates(
    audit: AuditResult,
    search_rows: list[dict[str, Any]],
) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for issue in audit.issues:
        if not issue.url or issue.url.startswith(","):
            continue
        candidates.append(
            {
                "page": issue.url,
                "reason": f"Technical finding `{issue.code}`: {issue.message}",
                "evidence": "Local static-site audit",
                "risk": "Review locally; do not deploy automatically.",
            }
        )
        if len(candidates) == 2:
            return candidates

    performance: dict[str, dict[str, float]] = {}
    for row in search_rows:
        page = str(row.get("page") or row.get("url") or "").strip()
        if not page:
            continue
        impressions = normalize_number(row.get("impressions"))
        position = normalize_number(row.get("position") or row.get("average_position"))
        clicks = normalize_number(row.get("clicks"))
        if impressions is None or position is None:
            continue
        current = performance.setdefault(page, {"impressions": 0.0, "clicks": 0.0, "position_sum": 0.0, "rows": 0.0})
        current["impressions"] += impressions
        current["clicks"] += clicks or 0.0
        current["position_sum"] += position
        current["rows"] += 1.0
    ranked: list[tuple[float, str, dict[str, float]]] = []
    for page, values in performance.items():
        position = values["position_sum"] / max(values["rows"], 1.0)
        if 8.0 <= position <= 30.0 and values["impressions"] > 0:
            ranked.append((values["impressions"], page, {**values, "position": position}))
    for _score, page, values in sorted(ranked, reverse=True)[:2]:
        candidates.append(
            {
                "page": page,
                "reason": "The connected export shows impressions with an average position between 8 and 30.",
                "evidence": (
                    f"Impressions {values['impressions']:.0f}; clicks {values['clicks']:.0f}; "
                    f"average position {values['position']:.1f}."
                ),
                "risk": "Confirm search intent and business accuracy before any title, answer, CTA, or schema edit.",
            }
        )
    return candidates[:2]


def weekly_report(
    audit: AuditResult,
    search_status: str,
    search_rows: list[dict[str, Any]],
    conversion_status: str,
    report_path: Path,
) -> None:
    generated = now_china()
    iso_year, iso_week, _weekday = generated.isocalendar()
    candidates = weekly_candidates(audit, search_rows)
    lines = [
        f"# Weekly SEO Review — {iso_year}-W{iso_week:02d}",
        "",
        f"- **Generated:** {generated.strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "- **Operation mode:** Analysis and recommendations only",
        "- **Automatic page edits:** None",
        "- **Automatic deployment:** Disabled",
        f"- **Google/Bing performance source:** {search_status}",
        f"- **Conversion-event source:** {conversion_status}",
        "",
        "No unavailable metric is reported as zero. A sitemap submission, discovered URL, crawl, index, impression, click, and enquiry are separate states.",
        "",
        "## 28-Day Comparison",
        "",
    ]
    if not search_rows:
        lines.append("- 未连接 (Not connected). A current 28-day versus previous 28-day comparison cannot be produced without an authorized export.")
    else:
        lines.append(f"- A connected export with {len(search_rows)} row(s) is available. Validate its date ranges before treating it as a complete 28-day comparison.")
    lines.extend(
        [
            "",
            "## Technical Review",
            "",
            *issue_lines(audit.issues),
            "",
            "## Optimization Candidates (Maximum 2)",
            "",
        ]
    )
    if candidates:
        for index, candidate in enumerate(candidates, start=1):
            lines.extend(
                [
                    f"### {index}. {candidate['page']}",
                    "",
                    f"- **Evidence:** {candidate['evidence']}",
                    f"- **Reason:** {candidate['reason']}",
                    "- **Allowed scope after review:** title, meta description, opening answer, internal link, visible FAQ, CTA, or matching structured data.",
                    "- **Expected impact:** Better technical clarity or closer alignment with demonstrated search intent; no ranking or enquiry outcome is guaranteed.",
                    f"- **Risk:** {candidate['risk']}",
                    "- **Observation period:** Review after at least 28 days of comparable data.",
                    "",
                ]
            )
    else:
        lines.append("- No page is selected. Without connected performance data or a current technical defect, the task will not invent an optimization target.")
    lines.extend(
        [
            "",
            "## Content",
            "",
            "- No article was generated or published.",
            "- At most one content update or one new article draft may be prepared after human approval and fact review.",
            "",
            "## Safety Record",
            "",
            "- No public copy, company facts, service scope, route, pricing, or legal information was changed.",
            "- No email, forum post, directory submission, indexing request, commit, merge, or deployment was performed.",
        ]
    )
    write_report(report_path, "\n".join(lines))


def monthly_report(
    audit: AuditResult,
    search_status: str,
    search_rows: list[dict[str, Any]],
    conversion_status: str,
    conversion_rows: list[dict[str, Any]],
    report_path: Path,
) -> None:
    generated = now_china()
    metric_state = (
        f"Connected export available ({len(search_rows)} row(s)); date coverage must be verified."
        if search_rows
        else "未连接 (Not connected)"
    )
    conversion_state = (
        f"Connected export available ({len(conversion_rows)} row(s)); event definitions must be verified."
        if conversion_rows
        else "未连接 (Not connected)"
    )
    priorities: list[str] = []
    for issue in audit.issues[:3]:
        priorities.append(f"Review `{issue.code}`" + (f" on {issue.url}" if issue.url else "") + f": {issue.message}")
    if not priorities:
        priorities.append("Maintain the current technical baseline and connect approved search-performance exports before data-led changes.")

    lines = [
        f"# Monthly SEO and Enquiry Report — {generated.strftime('%Y-%m')}",
        "",
        f"- **Generated:** {generated.strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "- **Operation mode:** Report only",
        "- **Automatic deployment:** Disabled",
        f"- **Search data:** {search_status}",
        f"- **Conversion data:** {conversion_status}",
        "",
        "## Search Visibility",
        "",
        f"- Indexing trend: {metric_state}",
        f"- Impressions trend: {metric_state}",
        f"- Click trend: {metric_state}",
        f"- CTR: {metric_state}",
        f"- Keyword position ranges: {metric_state}",
        f"- Brand versus non-brand queries: {metric_state}",
        f"- Commercial versus informational queries: {metric_state}",
        f"- Country distribution: {metric_state}",
        f"- Device distribution: {metric_state}",
        f"- Best and declining pages: {metric_state}",
        f"- New and disappeared queries: {metric_state}",
        "",
        "## Enquiry Events",
        "",
        f"- project_brief_start: {conversion_state}",
        f"- project_brief_submit: {conversion_state}",
        f"- email_click: {conversion_state}",
        f"- whatsapp_click: {conversion_state}",
        "- wechat_copy: NOT APPLICABLE — no verified company WeChat contact is published.",
        f"- service_cta_click: {conversion_state}",
        "",
        "The secure form may report `project_brief_submit` only after `/api/contact` returns its documented successful response. Email and messaging-link clicks still do not prove that a message was sent or received.",
        "",
        "## Technical Findings",
        "",
        *issue_lines(audit.issues),
        "",
        "## Content Update Effect",
        "",
        "- Not evaluated without a verified change log and comparable search data.",
        "",
        "## External Brand Opportunities",
        "",
        "- No external outreach or publication was performed. Any brand profile, directory, interview, or guest-content action requires human approval.",
        "",
        "## Priorities for Next Month (Maximum 3)",
        "",
        *[f"- {item}" for item in priorities[:3]],
        "",
        "## Monthly Limits",
        "",
        "- Page optimization tasks proposed: no more than 3.",
        "- Content drafts proposed: no more than 1.",
        "- Brand or off-page action proposed: no more than 1.",
        "- No content, outreach, sitemap submission, indexing request, commit, or deployment was performed.",
    ]
    write_report(report_path, "\n".join(lines))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("daily", "weekly", "monthly"):
        child = subparsers.add_parser(command)
        child.add_argument("--site-dir", help="Static site directory; auto-detected when omitted")
        child.add_argument("--report-root", help="Report root; defaults to seo/reports")
        child.add_argument("--search-console-data", help="Optional Google Search Console CSV/JSON export")
        child.add_argument("--bing-data", help="Optional Bing Webmaster Tools CSV/JSON export")
        child.add_argument("--conversion-data", help="Optional approved conversion-event CSV/JSON export")
    daily = subparsers.choices["daily"]
    daily.add_argument("--base-url", default=CANONICAL_ORIGIN)
    daily.add_argument("--local-only", action="store_true", help="Skip network and TLS checks")
    daily.add_argument("--strict", action="store_true", help="Exit non-zero after completing all checks if errors exist")
    daily.add_argument("--state-file", help="Previous-state JSON used to identify new and restored issues")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    site_dir = find_site_dir(args.site_dir)
    report_root = Path(args.report_root).expanduser().resolve() if args.report_root else DEFAULT_REPORT_ROOT
    audit = audit_local(site_dir)
    search_console_status, search_console_rows = optional_data_status(
        args.search_console_data,
        PROJECT_ROOT / "seo" / "data" / "search-console.json",
        "search_console",
    )
    bing_status, bing_rows = optional_data_status(
        args.bing_data,
        PROJECT_ROOT / "seo" / "data" / "bing.json",
        "bing",
    )
    conversion_status, conversion_rows = optional_data_status(
        args.conversion_data,
        PROJECT_ROOT / "seo" / "data" / "conversion-events.json",
        "conversion",
    )
    audit.search_console_status = search_console_status
    audit.bing_status = bing_status
    search_rows = [
        {**row, "_source": "Google Search Console"} for row in search_console_rows
    ] + [
        {**row, "_source": "Bing Webmaster Tools"} for row in bing_rows
    ]
    search_status = (
        f"Google Search Console: {search_console_status}; "
        f"Bing Webmaster Tools: {bing_status}"
    )

    generated = now_china()
    if args.command == "daily":
        if not args.local_only:
            add_live_checks(audit, args.base_url)
        state_path = Path(args.state_file).expanduser().resolve() if args.state_file else DEFAULT_STATE_FILE
        report_path = report_root / "daily" / f"{generated.date().isoformat()}.md"
        daily_report(audit, report_path, state_path, not args.local_only)
        print(f"Daily report: {report_path}")
        error_count = sum(issue.severity == "error" for issue in audit.issues)
        warning_count = sum(issue.severity == "warning" for issue in audit.issues)
        print(f"Checked {audit.sitemap_url_count} sitemap URLs; errors={error_count}; warnings={warning_count}")
        return 1 if args.strict and error_count else 0

    if args.command == "weekly":
        iso_year, iso_week, _weekday = generated.isocalendar()
        report_path = report_root / "weekly" / f"{iso_year}-W{iso_week:02d}.md"
        weekly_report(audit, search_status, search_rows, conversion_status, report_path)
        print(f"Weekly report: {report_path}")
        return 0

    report_path = report_root / "monthly" / f"{generated.strftime('%Y-%m')}.md"
    monthly_report(
        audit,
        search_status,
        search_rows,
        conversion_status,
        conversion_rows,
        report_path,
    )
    print(f"Monthly report: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
