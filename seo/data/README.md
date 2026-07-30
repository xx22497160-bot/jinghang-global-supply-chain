# Optional Report Inputs

This directory intentionally contains no fake analytics data.

The read-only automation reports `未连接 (Not connected)` when an authorized export is unavailable. It must never replace missing impressions, clicks, indexed pages, positions, or enquiry events with zero.

Optional inputs:

- `search-console.json`: redacted Google Search Console export, as a JSON list or `{"rows": [...]}`.
- `bing.json`: redacted Bing Webmaster Tools export, as a JSON list or `{"rows": [...]}`.
- `conversion-events.json`: approved aggregate conversion-event export, as a JSON list or `{"rows": [...]}`.

CSV or JSON paths may also be passed with `--search-console-data`, `--bing-data`, and `--conversion-data`.

Do not place passwords, API keys, OAuth tokens, cookies, Turnstile tokens, Cloudflare bindings, raw enquiry text, email addresses, phone numbers, product details, supplier details, or cargo details here.
