# Privacy-Friendly Analytics Options

## Current Baseline

The checked-in site does not include Google Analytics, Meta Pixel, Microsoft Clarity, session recording, or another marketing analytics script. The Privacy Notice explicitly reflects that state. Search and conversion data must therefore be reported as `未连接 (Not connected)` unless an authorized export or approved measurement source is actually available.

The 2026-07-29 production PageSpeed run detected an attempted Cloudflare Web Analytics beacon injection from `static.cloudflareinsights.com`. The site's strict Content Security Policy blocked that script, so the audit does not treat it as an enabled measurement source. The preferred current action is to disable the Cloudflare Web Analytics injection in the Cloudflare dashboard. Do not add the beacon origin to CSP unless analytics is explicitly approved and the Privacy Notice is updated first.

No option below is enabled by this document.

## Option 0 — Keep Measurement Disabled

**What it provides**

- No website analytics collection added by Jinghang.
- Search performance can still be reviewed through manually authorized Google Search Console and Bing Webmaster Tools exports.
- Enquiries can be reviewed from the receiving mailbox without creating a web analytics profile.

**Limitations**

- No reliable page-view, CTA, or funnel data.
- Mailbox activity must not be converted into website funnel claims without a defined manual process.

**Privacy work**

- No analytics-related Privacy Notice change is required while the implementation remains unchanged.

## Option 1 — Minimal First-Party Conversion Events

**Recommended only after explicit approval.**

A same-origin Cloudflare Pages Function or Worker could accept only the approved event names and minimal page context. It must not receive enquiry-form values. Aggregate reports can then distinguish:

- `project_brief_start`
- `project_brief_submit`
- `email_click`
- `whatsapp_click`
- `wechat_copy` only after a company WeChat contact is fact-verified and approved
- `service_cta_click`

**Safeguards**

- Keep event payloads free of names, contact details, company data, product data, supplier data, cargo data, route data, and free text.
- Fire `project_brief_submit` only after `/api/contact` returns a documented success response.
- Define retention, access, deletion, rate limiting, and bot filtering before launch.
- Review whether a cookie or persistent identifier is necessary; prefer aggregate, cookieless measurement.
- Update the Privacy Notice before production enablement.
- Keep endpoint credentials and infrastructure bindings outside source, reports, and logs.

**Trade-off**

This provides the most useful enquiry-path data with the smallest disclosed data set, but it still creates a new data-processing purpose that requires owner approval and privacy review.

## Option 2 — Cloudflare Web Analytics

Cloudflare Web Analytics may provide privacy-oriented aggregate traffic measurement and may fit the existing hosting stack. Current product features, data processing, retention, jurisdictional requirements, CSP changes, and support for the approved custom conversion events must be verified at the time of implementation.

This option is not approved or enabled by the repository. The production injection attempt observed on 2026-07-29 is blocked by CSP and should be disabled at account level until approval and privacy review are complete.

**Strengths**

- Operationally close to the existing Cloudflare deployment.
- Can provide aggregate traffic context without an advertising platform.

**Limits**

- Page traffic alone does not prove an enquiry.
- Custom conversion-event support and implementation details must be verified before selection.
- The Privacy Notice and any required consent controls must be reviewed before enablement.

## Option 3 — Privacy-Oriented Dedicated Analytics

Products such as Plausible or a carefully configured Matomo deployment can provide aggregate page and custom-event reporting.

**Review before selection**

- hosting location and data processor
- cookie and identifier behavior
- retention and deletion
- data-processing agreement
- CSP and script loading
- custom event behavior
- cost and maintenance
- applicable consent requirements

Do not send enquiry-form fields to these services.

## Option 4 — GA4 or Advertising Analytics

Do not enable by default. GA4 or advertising pixels should be considered only when there is a clear commercial need, explicit approval, a documented consent and privacy approach, and a reviewed event/data-retention design.

This option creates the greatest risk of unnecessary tracking and accidental disclosure. Product, supplier, cargo, route, form, and contact details must never be included in analytics parameters.

## Recommended Decision

Keep analytics disabled until an owner approves a purpose and privacy change. If measurement is approved, begin with Option 1 or a verified aggregate Cloudflare option, collect only the currently applicable defined events, keep unverified contact-channel events disabled, and exclude all enquiry content.

## Search-Platform Data

Google Search Console and Bing Webmaster Tools are search-performance sources, not behavioural analytics. Their states must be reported separately:

- discovered
- crawled
- indexed
- impressions
- clicks
- enquiries

One state must never be used as evidence of another.

## Data Import for Local Reports

The read-only SEO script accepts optional CSV or JSON exports. Missing files produce `未连接 (Not connected)`.

- Google Search Console export: `seo/data/search-console.json` or a path passed by command line
- Bing Webmaster Tools export: `seo/data/bing.json` or a path passed by command line
- Conversion export: `seo/data/conversion-events.json` or a path passed by command line

Do not commit account credentials, API keys, OAuth tokens, cookies, raw enquiry content, or exported personal data. Aggregate and redact an export before using it for local reporting.
