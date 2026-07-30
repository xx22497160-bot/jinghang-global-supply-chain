# Jinghang Global Supply Chain — Baseline SEO Technical Audit

Audit date: 2026-07-29 (Asia/Shanghai)

Production site: `https://jinghangsc.com/`

Authoritative local source: `work/github-main`
Audited Git revision: `8ca2f4b` (`main`, matching `origin/main` at audit start)

## Executive Summary

The current production baseline is a lightweight English-first static website deployed through GitHub-connected Cloudflare Pages. It has 15 canonical, indexable public URLs, five focused service pages, three Insights articles, Cloudflare Pages Functions for the contact form, and no marketing analytics or session-recording script.

All 15 Sitemap URLs rendered successfully in Chrome at their expected production URLs on 2026-07-29. Their live Title, Meta Description, H1, canonical, language, Open Graph data, Twitter Card data, and JSON-LD types matched the authoritative `work/github-main` source. Exact response headers and status codes could not be captured in the available command-line environment, so this audit does not convert a successful browser render into an unverified `200` claim.

The baseline has no local internal broken links, invalid internal anchors, orphan pages, duplicate Titles, duplicate Meta Descriptions, duplicate H1s, or duplicate canonicals. All 15 intended public pages are present once in `sitemap.xml`, use the `https://jinghangsc.com` host, have one H1, contain English text in the initial static HTML, and contain parseable JSON-LD.

The main open risks are an unverified LinkedIn URL published visibly and in `Person.sameAs`, incomplete full-brand usage in several Title and Open Graph titles, missing Breadcrumb markup on the FAQ page, two stale Sitemap `lastmod` dates, and several measurement gaps that must remain labelled “not connected” or “not verified.”

## Source-of-Truth Decision

The older local copy under `english_website_project/site` is not the current production source and was excluded from page-level audit results. It contains only 10 indexable routes and lacks the five specialist service pages now present in production.

The current source is the GitHub `main` clone at `work/github-main`, commit `8ca2f4b`. Production metadata and structured-data signatures matched this source for all 15 canonical URLs.

No unrelated project file, keyword, host, Sitemap entry, or report was used in this audit.

## Current Architecture

| Area | Current implementation |
|---|---|
| Framework | None |
| Rendering | Static semantic HTML; core copy is present in the initial HTML |
| Public pages | 15 canonical indexable URLs plus a custom noindex 404 page |
| Styling | One same-origin stylesheet, approximately 36 KB |
| Client JavaScript | Contact page only; one deferred same-origin file, approximately 7 KB |
| Form processing | Cloudflare Pages Functions, server-side validation, Turnstile verification, and a private mailer service binding |
| Hosting | GitHub-connected Cloudflare Pages |
| Production branch | `main` |
| Build command | None |
| Output directory | Repository root |
| Analytics | No GA4, Meta Pixel, Clarity, or session-recording script found |
| CI/CD at audited commit | Cloudflare Pages deployment is documented; no committed GitHub Actions workflow was present at the audited commit |
| Google ownership | Repository evidence says the URL-prefix property was verified on 2026-07-21 |
| Bing ownership | Verification meta tag is present; repository evidence says portal verification was not confirmed |
| IndexNow | Root key file exists; no current submission log was available at audit start |

## Canonical Host and Redirect Observations

The existing canonical version should remain:

`https://jinghangsc.com/`

This version is consistently used by:

- all 15 canonical tags;
- all 15 Open Graph URLs;
- all Sitemap entries;
- Organization, WebSite, WebPage, Service, Article, FAQPage, and Breadcrumb identifiers;
- internal absolute links found in the static source;
- `robots.txt` Sitemap declaration.

Browser navigation produced the following final URLs:

| Requested version | Browser final URL | Observation |
|---|---|---|
| `http://jinghangsc.com/` | `https://jinghangsc.com/` | Canonical HTTPS/non-www host reached |
| `https://jinghangsc.com/` | `https://jinghangsc.com/` | Canonical version |
| `http://www.jinghangsc.com/` | `https://jinghangsc.com/` | Canonical HTTPS/non-www host reached |
| `https://www.jinghangsc.com/` | `https://jinghangsc.com/` | Canonical HTTPS/non-www host reached |
| `https://jinghangsc.com/services/` | `https://jinghangsc.com/services` | Trailing slash consolidated |
| `https://jinghangsc.com/services.html` | `https://jinghangsc.com/services` | HTML filename consolidated |
| `https://jinghangsc.com/index.html` | `https://jinghangsc.com/` | Homepage filename consolidated |
| `https://jinghangsc.com/services?utm_source=seo-audit` | Same parameter URL | Clean canonical points to `/services` |
| `https://jinghangsc.com/SERVICES` | Same uppercase URL | Custom noindex 404 document rendered |

The browser confirms the final destination but does not expose the redirect response code or complete redirect chain in this environment. Therefore, the required permanent status (`301` or equivalent permanent redirect) and single-hop behaviour still require a network-enabled header check.

## Crawlability and Indexability

### Robots

The audited source `robots.txt`:

- allows `OAI-SearchBot`;
- allows `PerplexityBot`;
- allows all other user agents;
- does not block public paths;
- declares `https://jinghangsc.com/sitemap.xml`.

Direct live retrieval of the text asset was blocked by the local browser client, and command-line DNS was unavailable. This is an audit-environment limitation, not evidence that the live file is missing.

### Sitemap

The source Sitemap contains exactly 15 URLs:

- all use the canonical HTTPS/non-www host;
- all correspond to real static pages;
- no redirect URL, parameter URL, verification file, preview host, test page, or 404 page is included;
- no intended public route is missing;
- no URL is duplicated.

The `lastmod` value is `2026-07-21` for every URL. Git history shows that `contact.html` and `privacy.html` were last materially updated on `2026-07-22`; those two `lastmod` values should be corrected when the next verified Sitemap update is made.

### Meta Robots and X-Robots-Tag

- None of the 15 intended public pages contains `noindex`; absence of a robots meta tag leaves the normal index/follow default.
- `404.html` contains `noindex`.
- The retired internal Cloudflare mailer route returns a real `404` with `X-Robots-Tag: noindex` in the source Function.
- No global `X-Robots-Tag` is configured in `_headers`.
- Live response-level `X-Robots-Tag` values were not directly observable in this environment.

## Page-Level Findings

The full row-level inventory is in `seo/url-inventory.csv`.

Baseline totals:

- 15 canonical public URLs;
- 15 pages in the Sitemap;
- 15 unique Titles;
- 15 unique Meta Descriptions;
- 15 unique H1s;
- 15 unique canonicals;
- 0 orphan pages;
- 0 broken internal page links;
- 0 invalid internal fragment targets;
- 0 JSON-LD parse errors;
- 0 HTML `<img>` elements, so HTML image-alt coverage is not applicable;
- Open Graph and Twitter Card fields are complete on all 15 pages;
- `og:image:alt` and `twitter:image:alt` are present on all 15 pages.

The pages use a shared 1200 × 630 Open Graph image and a 512 × 512 logo asset. Neither asset is loaded as visible page content.

### Static Content

Core content is present in the initial static HTML. Source-level main-page word counts range from 346 words on `/insights/` to 1,921 words on the longest guide. Collapsed `<details>` answers are present in the HTML but are not always counted by browser `innerText`; source counts are therefore the primary inventory measurement.

No pair of page main-content word sets exceeded a 55% Jaccard similarity threshold. This is a screening result, not a substitute for editorial duplicate-intent review.

### Structured Data

Observed JSON-LD families:

- Home: `Organization`, `WebSite`, `WebPage`;
- five specialist service pages: `WebPage`, `Service`, `BreadcrumbList`, `FAQPage`;
- Insights articles: `Article`, `WebPage`, `BreadcrumbList`, `FAQPage`;
- Insights index: `WebPage`, `BreadcrumbList`, `ItemList`;
- About: `AboutPage`, `Person`, `BreadcrumbList`;
- Contact: `ContactPage`, `BreadcrumbList`;
- Privacy: `WebPage`, `BreadcrumbList`;
- FAQ: `FAQPage`.

All JSON-LD parsed successfully. The FAQ page lacks the otherwise consistent visible breadcrumb and `BreadcrumbList` entity.

The About page publishes a LinkedIn profile both as a visible link and in `Person.sameAs`. Project memory explicitly states that no LinkedIn URL is verified. This must be verified and added to memory or removed from public content and schema.

## Internal and External Links

All public URLs have inbound internal links. Every top-level page is linked from 14 other public pages. The three Insights articles have inbound links from five, five, and six distinct public pages respectively.

No broken internal route or invalid fragment target was found in the static source.

External web destinations found:

- ICC Incoterms® 2020 official page — live and readable;
- ICC Academy DAP/DDP article — live and readable;
- WhatsApp `wa.me` contact link — destination could not be independently read by the audit tool;
- LinkedIn profile — destination could not be independently verified and conflicts with the verified-memory baseline.

External backlinks to Jinghang were not measured. No connected Search Console link report, Bing report, or third-party backlink dataset was available. This value must remain “not connected,” not zero.

## 404 and Duplicate-URL Behaviour

A deliberately nonexistent production path rendered the custom “Page Not Found” document with:

- Title: `Page Not Found | Jinghang Global Supply Chain`;
- one H1: `That page could not be found.`;
- `noindex`;
- no canonical.

This is appropriate content for a hard 404. Exact response status was not exposed by the browser, so the audit cannot independently prove the required HTTP `404` response rather than a soft 404.

Uppercase `/SERVICES` rendered the same noindex 404 document. Trailing-slash, `.html`, and `/index.html` variants consolidated to clean URLs. A test UTM parameter remained in the address bar but canonicalized to the clean page, avoiding a separate canonical target.

## Mobile and Performance Baseline

A browser viewport check at a nominal 390 × 844 mobile size showed:

- homepage document width equalled viewport width;
- contact page document width equalled viewport width;
- no horizontal overflow on those representative templates;
- desktop navigation hidden and mobile navigation displayed on the homepage;
- the contact form fit within the mobile viewport.

Static performance indicators are favourable:

- no external webfont request;
- no visible HTML image payload;
- one shared stylesheet of approximately 36 KB;
- JavaScript limited to the contact page and deferred;
- contact JavaScript approximately 7 KB;
- Open Graph image approximately 68 KB and not part of normal page rendering.

Lighthouse, CrUX, Core Web Vitals, and response-timing data were not available in this audit environment. Static asset size and absence of overflow are not substitutes for those measurements.

## Search Discovery and Measurement Status

Repository evidence records:

- Google Search Console URL-prefix verification on 2026-07-21;
- a successful Sitemap submission reporting 15 **discovered** pages on 2026-07-21;
- homepage and five service URLs submitted to Google’s priority crawl queue;
- Bing verification meta tag present;
- Bing portal verification not confirmed at that time;
- an IndexNow key file present.

No current Search Console or Bing account/API connection was available during this audit. Therefore the following are unknown:

- current crawl status;
- current indexed URL count;
- impressions;
- clicks;
- CTR;
- average position;
- search queries;
- countries and devices;
- backlink data;
- enquiries attributable to organic search.

“Discovered,” “crawled,” “indexed,” “received impressions,” “received clicks,” and “generated an enquiry” remain separate states. No ranking or enquiry claim is made.

## Priority Issues

See `seo/technical-issues.csv` for evidence and recommended resolution.

1. Verify or remove the LinkedIn profile and `sameAs` reference.
2. Use the full `Jinghang Global Supply Chain` brand consistently in Title and Open Graph title strategy where current pages omit it or use only “Jinghang.”
3. Add a visible breadcrumb and matching `BreadcrumbList` to `/faq`.
4. Correct the two stale Sitemap `lastmod` dates after confirming the intended release.
5. Restore the missing validator referenced by README, or update the documentation to the real validation command.
6. Run a network-enabled header audit and Lighthouse test.
7. Connect or export current Search Console and Bing data before making index, ranking, traffic, or CTR claims.

## Audit Limitations

- Command-line DNS resolution for `jinghangsc.com` was unavailable in the execution sandbox.
- Chrome rendered every public page and confirmed final URLs and DOM-level signals, but did not expose exact response codes, redirect hop counts, or response headers.
- Direct browser retrieval of live `robots.txt` and `sitemap.xml` was blocked by the client. Their source content and repository history were audited.
- Search Console, Bing Webmaster Tools, Cloudflare analytics, and backlink datasets were not connected.
- No Lighthouse or field-performance dataset was available.

These limitations are explicitly recorded so missing data is not converted into a false zero or success claim.

## Local Remediation and Later Measurement

After the immutable baseline above was recorded, the local working tree removed the unverified LinkedIn link and `sameAs`, added visible and structured breadcrumbs to the FAQ, synchronized full-brand metadata, corrected meaningful Sitemap dates, added direct-answer modules to Home and Services, and restored a repository-local validation command. The strict local audit then passed 15 Sitemap URLs with zero errors and zero warnings.

An official PageSpeed Insights run completed at 17:22 China Standard Time on 2026-07-29. Both mobile and desktop scored 100 Performance, 100 Accessibility, 92 Best Practices, and 100 SEO. Mobile FCP, LCP, and Speed Index were 1.5 seconds with 0 ms TBT and 0 CLS. Desktop FCP, LCP, and Speed Index were 0.4 seconds with 0 ms TBT and 0 CLS. No field-user data was available.

The Best Practices deduction came from an attempted Cloudflare Web Analytics beacon injection that the strict CSP blocked. The local release does not whitelist the beacon. Disabling the Cloudflare Web Analytics injection at account level is the privacy-aligned manual action; analytics must not be enabled without explicit approval and a Privacy Notice update. See `seo/performance-audit.md`.

## Static Output Safety

Adding private audit reports and automation files makes repository-root deployment unsafe because those files could become publicly reachable. The local working tree now uses `python3 scripts/build_site.py` to copy an explicit allowlist of 27 public files into `dist/`; it excludes `seo/`, `memory/`, `.github/`, `scripts/`, `functions/`, and repository documentation from the static output.

Before any future push that can trigger Cloudflare Pages, the Pages project must be changed to use `python3 scripts/build_site.py` as its build command and `dist` as its build output directory. The `functions/` directory must remain at the repository root so Cloudflare Pages Functions can discover it. This dashboard change has not been made during the local-only audit.
