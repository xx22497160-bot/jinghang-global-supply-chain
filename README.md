# Jinghang SC Website

Static English website for Jinghang SC, the short name of Jinghang Global Supply Chain, positioned as a China supply chain coordination partner for international hardware startups, brands, and growing businesses.

Phase 2 adds a 60-question FAQ knowledge base, structured entity/page/service data, a practical Insights library, conversion-path improvements, and expanded technical SEO validation without changing the core visual system.

## Live Site

https://jinghangsc.com/

## Technology

- Semantic HTML
- One shared CSS file
- No JavaScript, package manager, framework, or build command
- GitHub-connected Cloudflare Pages deployment

## Cloudflare Pages Settings

- Framework preset: None
- Build command: leave blank
- Build output directory: `/`
- Production branch: `main`

## Main Routes

- `/`
- `/services`
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

From the local project root, run:

```bash
"/Users/bang/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3" work/validate_site.py
```

The Phase 2 release expects 11 HTML files, 10 indexable routes, at least 50 visible FAQs, exact visible/schema FAQ parity, all required Schema.org families, current CSP hashes, complete social metadata, and valid internal routes and anchors.

## Analytics Status

No analytics or session-recording ID is currently embedded. Search Console, GA4, Microsoft Clarity, Bing Webmaster Tools, or Cloudflare Web Analytics must use real account-issued identifiers or account authorization, followed by privacy/CSP review and live verification.
