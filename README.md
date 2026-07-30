# Jinghang Global Supply Chain Website

Static English website for Jinghang Global Supply Chain, positioned as a China-based supply chain partner for overseas businesses.

The specialist-page release adds five focused service decision pages, a 27-question fact-controlled FAQ, structured entity and service data, a practical Insights library, conversion paths, and technical SEO validation without changing the core visual system.

## Live Site

https://jinghangsc.com/

## Technology

- Semantic HTML
- One shared CSS file
- One small same-origin JavaScript file for the secure Contact-page submission flow
- Cloudflare Pages Functions for server-side validation and Turnstile verification
- A private Cloudflare service binding to the `jinghang-contact-mailer` Worker
- No package manager, framework, or tracking script
- A standard-library Python build step that copies only approved public files to `dist/`
- GitHub-connected Cloudflare Pages deployment

## Cloudflare Pages Settings

- Framework preset: None
- Build command: `python3 scripts/build_site.py`
- Build output directory: `dist`
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

The `_headers`, `robots.txt`, `sitemap.xml`, and `llms.txt` source files remain in the repository root and are copied to `dist/` by the allowlist build. The `functions/` directory remains at the Pages project root, outside the static output directory, as required for Pages Functions.

## Validation

From the repository root, run the public build and complete local-only validation:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_site.py
PYTHONDONTWRITEBYTECODE=1 python3 seo/scripts/seo_automation.py daily --local-only --strict
```

The current release expects the allowlisted `dist/` output to contain no internal SEO reports, data, scripts, GitHub configuration, memory, README, or Functions source. Source validation expects 16 public-template HTML files, 15 canonical indexable routes, exactly 27 verified visible FAQs with matching FAQPage entities, valid JSON-LD, current CSP hashes, complete social metadata, valid internal routes and assets, and no unverified public social-profile or messaging identifiers.

## Analytics Status

No analytics or session-recording ID is currently embedded. GA4, Microsoft Clarity, or Cloudflare Web Analytics must use real account-issued identifiers or account authorization, followed by privacy/CSP review and live verification.

The 2026-07-29 production PageSpeed audit observed an attempted Cloudflare Web Analytics beacon injection. The current Content Security Policy blocked it, and it is not treated as an approved measurement source. Disable that injection in the Cloudflare dashboard unless analytics is explicitly approved together with the required Privacy Notice and CSP changes.

## Search Discovery Status

- The Google Search Console URL-prefix property for `https://jinghangsc.com/` was verified on 2026-07-21 through `googlebdcd5011c88334e9.html`.
- `sitemap.xml` was submitted successfully in Search Console and reported 15 discovered pages on 2026-07-21.
- The home page and five specialist service URLs were submitted to Google's priority crawl queue after the release.
- The Bing verification meta tag is present on the home page. Bing Webmaster Tools created the site entry, but its verification request returned a platform-side unexpected/fetch error; do not describe the property as verified until the portal confirms it.
- `d20ec9908a240ebbdc5b5b295ea324b4.txt` is the root IndexNow key file. Keep it deployed if the key is used for future IndexNow notifications.

Verification files and tags must remain in place to preserve ownership or protocol validation.

## Contact Form Runtime

The form at `/contact` sends a same-origin JSON request to `/api/contact`. The Pages Function validates every field, verifies the single-use Turnstile token on the server, and then calls a private mailer Worker through the `CONTACT_MAILER` service binding. No form-submission database or visitor auto-reply is used.

Required Pages production settings:

- Variable `TURNSTILE_SITE_KEY`: public site key for the managed `jinghangsc.com` Turnstile widget
- Encrypted secret `TURNSTILE_SECRET_KEY`: matching server-side secret
- Service binding `CONTACT_MAILER`: target `jinghang-contact-mailer`

Required mailer Worker settings:

- Worker name `jinghang-contact-mailer`
- No public route and `workers.dev` disabled
- `send_email` binding `CONTACT_EMAIL`
- Encrypted Worker secret `CONTACT_DESTINATION`, set to the verified destination that receives `hello@jinghangsc.com`
- Fixed technical sender `website@jinghangsc.com`; visitor work email is used only as `Reply-To`

The mailer Worker must be maintained and deployed separately from the Pages static-output directory. Its destination secret is configured only in Cloudflare and must never be committed.

Deployment is incomplete until a real production enquiry arrives in Anna's inbox and Reply opens the visitor's address. Never add production secrets to Git or browser-side JavaScript.
