# Production Performance Audit

Audit target: `https://jinghangsc.com/`

Tool: Google PageSpeed Insights, Lighthouse 13.4.1

Report time: 2026-07-29 17:22 China Standard Time
Report: https://pagespeed.web.dev/analysis/https-jinghangsc-com/4fsko2v9w0

## Scope

This report measures the production version deployed before the current local release. The current task intentionally does not deploy. The local release adds visible HTML content and metadata but does not add a font, image, stylesheet, browser-side application bundle, marketing tracker, or other rendering dependency. A post-deployment run is still required before describing these scores as the result of the local release.

PageSpeed reported no field-user data for this URL. The figures below are Lighthouse lab estimates, not Core Web Vitals field evidence and not a ranking or conversion claim.

## Results

| Mode | Performance | Accessibility | Best Practices | SEO | Agentic Browsing |
|---|---:|---:|---:|---:|---:|
| Mobile | 100 | 100 | 92 | 100 | 3/3 |
| Desktop | 100 | 100 | 92 | 100 | 3/3 |

### Mobile lab metrics

- First Contentful Paint: 1.5 s
- Largest Contentful Paint: 1.5 s
- Speed Index: 1.5 s
- Total Blocking Time: 0 ms
- Cumulative Layout Shift: 0

### Desktop lab metrics

- First Contentful Paint: 0.4 s
- Largest Contentful Paint: 0.4 s
- Speed Index: 0.4 s
- Total Blocking Time: 0 ms
- Cumulative Layout Shift: 0

## Best Practices Finding

PageSpeed recorded an attempted request for Cloudflare's `static.cloudflareinsights.com/beacon.min.js`. The site's strict Content Security Policy blocked the script, creating a console error and the 92 Best Practices score.

The repository does not include or authorize a marketing analytics script, and the current Privacy Notice says no marketing analytics is enabled. Therefore:

1. Do not add `static.cloudflareinsights.com` to CSP.
2. Disable the Cloudflare Web Analytics injection in the Cloudflare dashboard.
3. If analytics is considered later, require explicit approval, a documented data-minimization plan, and a Privacy Notice update before enabling it.
4. Rerun PageSpeed after the Cloudflare setting change and again after this local release is deployed.

## Mobile Layout Check

Separate production checks at a mobile viewport confirmed:

- one H1 on Home and Contact;
- mobile navigation present;
- no horizontal overflow on Home or Contact;
- the primary Home CTA is 50 px high and spans the mobile content width;
- email and WhatsApp links use actionable `mailto:` and `wa.me` destinations;
- the secure form points to same-origin `/api/contact`.

The contact form's Turnstile container initialized in production. A real submission was not sent because that would create an external enquiry. End-to-end mailbox delivery remains a manual production test.
