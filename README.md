# Jinghang Global Supply Chain Website

Static English website for Jinghang Global Supply Chain, positioned as a China-based supply chain partner for overseas businesses.

The specialist-page release adds five focused service decision pages, a 27-question fact-controlled FAQ, structured entity and service data, a practical Insights library, conversion paths, and technical SEO validation without changing the core visual system.

## Live Site

https://jinghangsc.com/

## Technology

- Semantic HTML
- One shared CSS file
- One small same-origin JavaScript file that prepares the Contact-page email draft in the visitor's browser
- No package manager, framework, tracking script, or build command
- GitHub-connected Cloudflare Pages deployment

## Cloudflare Pages Settings

- Framework preset: None
- Build command: leave blank
- Build output directory: `/`
- Production branch: `main`

## Main Routes

- `/`
- `/services`
- `/china-sourcing`
- `/quality-inspection`
- `/freight-from-china`
- `/ddp-shipping-from-china`
- `/hardware-startup-supply-chain-china`
- `/about`
- `/faq`
- `/contact`
- `/privacy`
- `/insights/`
- `/insights/how-to-source-products-from-china-without-an-in-house-team`
- `/insights/china-supplier-evaluation-checklist`
- `/insights/ddp-vs-dap-shipping-from-china`

The `_headers`, `robots.txt`, `sitemap.xml`, and `llms.txt` files must remain in the repository root so Cloudflare Pages can deploy them with the site.

## Validation

From the AEO/GEO implementation workspace, run:

```bash
"/Users/bang/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3" work/validate_jinghang_site.py
```

The current release expects 16 HTML files, 15 indexable routes, exactly 27 verified visible FAQs with matching FAQPage entities, `WebPage`, `Service`, and `BreadcrumbList` schema on each specialist page, no schema `telephone` field, current CSP hashes, complete social metadata, and valid internal routes and anchors.

## Analytics Status

No analytics or session-recording ID is currently embedded. GA4, Microsoft Clarity, or Cloudflare Web Analytics must use real account-issued identifiers or account authorization, followed by privacy/CSP review and live verification.

## Search Discovery Status

- The Google Search Console URL-prefix property for `https://jinghangsc.com/` was verified on 2026-07-21 through `googlebdcd5011c88334e9.html`.
- `sitemap.xml` was submitted successfully in Search Console and reported 15 discovered pages on 2026-07-21.
- The home page and five specialist service URLs were submitted to Google's priority crawl queue after the release.
- The Bing verification meta tag is present on the home page. Bing Webmaster Tools created the site entry, but its verification request returned a platform-side unexpected/fetch error; do not describe the property as verified until the portal confirms it.
- `d20ec9908a240ebbdc5b5b295ea324b4.txt` is the root IndexNow key file. Keep it deployed if the key is used for future IndexNow notifications.

Verification files and tags must remain in place to preserve ownership or protocol validation.
