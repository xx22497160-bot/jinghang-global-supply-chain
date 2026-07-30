# Safe SEO Automation Architecture

## Detected Repository State

- Repository: Jinghang Global Supply Chain production website source
- Rendering: static HTML
- Hosting: GitHub-connected Cloudflare Pages
- Build step: `python3 scripts/build_site.py`
- Static output: `dist/`, populated from an explicit public-file allowlist
- Server-side contact path: Cloudflare Pages Functions and a private mailer service binding
- Existing GitHub Actions at the start of this audit: none
- Marketing analytics in source: none

This architecture is limited to the current company website and contains no unrelated project brand, route, page, sitemap, keyword, analytics, or deployment reference.

## Safety Model

The automation has read-only repository permissions and does not:

- edit public HTML or company facts;
- submit a sitemap or use the Google Indexing API;
- send IndexNow notifications without a real changed-URL workflow;
- publish an article or create location pages;
- send email, submit a form, contact a website, or perform outreach;
- commit, merge, push, release, or deploy;
- read or print Cloudflare, Search Console, Bing, email, or Turnstile credentials;
- report an unavailable metric as zero.

Scheduled reports are uploaded as GitHub Actions artifacts. They are not committed back to `main`.

The repository must not be deployed with `/` as the static output directory after the SEO files are committed. Cloudflare Pages must use `dist` as the build output directory so `seo/`, `.github/`, `scripts/`, `memory/`, README files, optional search exports, and Functions source are not exposed as static assets. The `functions/` directory remains at the Pages project root rather than inside `dist`, following the Pages Functions directory model.

## Local Script

`seo/scripts/seo_automation.py` has three subcommands:

### `daily`

- parses `sitemap.xml`;
- maps every sitemap URL to local static HTML;
- requires the current 15 canonical sitemap URLs;
- checks titles, descriptions, H1, canonical, robots meta, language, JSON-LD syntax, Open Graph, image alt attributes, internal links, static assets, duplicate metadata, test-domain references, `robots.txt`, and Sitemap declaration;
- compares visible FAQ questions and answers with their `FAQPage` entities and requires the current 27-question main FAQ;
- calculates every current inline-script SHA-256 hash and compares the exact set with the CSP hashes in `_headers`;
- checks that the secure Contact form still points to the same-origin Pages Function;
- rejects unverified social-profile/contact claims and cross-project runtime references;
- optionally checks live URL status, final URL, redirect hops, TLS certificate expiry, robots, Sitemap, the four apex/www HTTP/HTTPS variants, and test-domain references in live HTML;
- records but does not follow redirects to a host outside `jinghangsc.com` and `www.jinghangsc.com`;
- records new and restored issues when a previous state cache is available;
- continues after an individual page failure;
- never changes page copy.

Use `--local-only` to suppress network checks. Use `--strict` to return a non-zero status after all checks and report generation when an error exists.

### `weekly`

- reviews the local technical state;
- reads optional redacted Search Console and Bing exports;
- selects no more than two optimization candidates;
- does not edit those pages;
- does not create or publish content;
- states `未连接 (Not connected)` when data is unavailable.

### `monthly`

- generates a report only;
- leaves unavailable search and conversion metrics as `未连接 (Not connected)`;
- limits proposed priorities to three page tasks, one content draft, and one off-page action;
- does not perform any proposed action.

## Schedules

| Workflow | UTC | China Standard Time | Behaviour |
|---|---:|---:|---|
| `.github/workflows/seo-daily.yml` | Every day 01:30 | Every day 09:30 | Monitor only |
| `.github/workflows/seo-weekly.yml` | Monday 01:30 | Monday 09:30 | Analyze and recommend no more than two pages |
| `.github/workflows/seo-monthly.yml` | Day 1, 01:30 | Day 1, 09:30 | Report only |

All workflows support `workflow_dispatch`.

## Data Connections

No Search Console, Bing, or conversion-event API credential is present or required. Optional redacted exports can be supplied as:

- `seo/data/search-console.json`
- `seo/data/bing.json`
- `seo/data/conversion-events.json`

Missing files do not fail the automation. The report says `未连接 (Not connected)` and does not synthesize a value.

`seo/data/.gitignore` excludes CSV and JSON exports by default. Keep raw or redacted platform exports local unless a separately reviewed, non-sensitive aggregate fixture is intentionally approved.

## State and Rollback

The daily issue-state file is generated at `seo/state/daily-latest.json`, ignored by Git, and persisted between scheduled runs through a GitHub Actions cache. Generated reports are retained as workflow artifacts.

Because public files are not changed, rollback is limited to removing or disabling the relevant workflow. There is no automatic content rollback or deployment path.

## Failure Behaviour

- One page failure is recorded and the monitor continues with the remaining pages.
- The daily report and state are uploaded even when a critical check fails.
- The daily workflow fails only after report creation, making the problem visible without losing evidence.
- Missing optional search or analytics data does not fail any workflow.
- Weekly and monthly tasks do not fail solely because performance data is unavailable.
