# Jinghang Content Gap Analysis

Audit date: 2026-07-29

Scope: local source in `work/github-main`

Canonical host used for mapping: `https://jinghangsc.com`
Search-platform data connection in this run: **NOT CONNECTED**

## Evidence boundary

This analysis uses the checked-out website, its 15 canonical indexable URLs, `AGENTS.md`, and every file in the workspace `memory/` folder. It does not use Google Search Console, Bing Webmaster Tools, analytics, sales-pipeline, or keyword-volume data. Therefore:

- no page is described as indexed, ranking, receiving impressions, receiving clicks, or generating enquiries;
- priorities are based on visible buyer intent, current site architecture, and verified service scope—not on measured search demand;
- an absent platform metric is **unknown**, not zero;
- no route, fee, transit time, warehouse ownership, inspection result, customs result, or customer outcome has been inferred.

The repository records a previous Google verification and submission event and an unresolved Bing verification attempt. Those historical notes were not revalidated in an authenticated portal during this run.

## Current content architecture

The local source contains:

- 1 homepage;
- 1 service hub;
- 5 distinct specialist service pages;
- 1 About page;
- 1 FAQ page with 27 fact-controlled answers;
- 1 Contact page;
- 1 Privacy page;
- 1 Insights hub;
- 3 substantial Insights guides.

The five specialist pages already cover the major commercial intents requested in the brief:

| Page | Primary intent | Collision control |
|---|---|---|
| `/china-sourcing` | China sourcing services | Transactional service page; the sourcing Insight remains an informational operating guide. |
| `/quality-inspection` | Pre-shipment quality inspection in China | Owns the service intent; the supplier checklist only supports evaluation and release planning. |
| `/freight-from-china` | Freight from China | Owns transport-mode and route-review intent. |
| `/ddp-shipping-from-china` | DDP shipping from China | Owns transactional DDP review; the DDP-vs-DAP Insight owns comparison intent. |
| `/hardware-startup-supply-chain-china` | China supply chain for hardware startups | Owns audience-specific commercial intent. |

This separation is sound. Do not collapse the pages into the service hub, and do not create near-duplicate country or city variants.

## Priority content gaps

### P0 — Connect real performance data before making ranking-led changes

The most important gap is evidence, not page count. No authenticated Google or Bing performance data is connected to this run. Before rewriting pages for CTR or rankings, export or connect:

- query, page, country, and device data for the latest 28 days;
- the preceding 28-day comparison period;
- indexing and crawl reasons for the 15 canonical URLs;
- enquiry-event data only after a privacy-approved measurement design is implemented.

Do not interpret sitemap discovery as indexing, indexing as ranking, an impression as a click, or a click as an enquiry.

### P0 — Stable metadata on three commercial pages

The pages are already substantial. The main metadata gaps are narrow:

1. `/ddp-shipping-from-china` uses a title centered on the United States and “25 European Countries,” which omits verified Canada and Australia availability and makes a route count the primary label. Use a stable service title and keep current route scope in visible copy.
2. `/freight-from-china` and `/hardware-startup-supply-chain-china` use the shortened “Jinghang” label in the title. The full public brand is safer for entity disambiguation.
3. `/about` repeats the homepage's broad “China Supply Chain Partner” H1. A branded About H1 would better separate trust intent from homepage commercial intent.

These are small edits, not reasons to rewrite the pages.

### P1 — One high-intent supporting guide

The best next draft is:

> **Information Needed for a Freight Quote From China**

Why this gap is worth filling:

- it answers a repeated pre-enquiry question with a concrete checklist;
- it supports `/freight-from-china` without targeting the same primary keyword;
- it helps prospects prepare the fields already requested on `/contact`;
- it can qualify leads without promising a route, price, timing, or cargo acceptance;
- it provides a natural next step to the route-review CTA.

Only a brief has been created. It must not be published automatically.

### P1 — A visible editorial review convention

The three Insights guides contain publication and modified dates in metadata and use the organization as author. The pages would benefit from a consistent visible editorial convention, but only after the company approves it. Possible fields are:

- Published date;
- Last reviewed date;
- Authoring organization;
- Named reviewer only if the person's role and review are verified;
- Scope note and external official sources where the topic is legally or operationally time-sensitive.

Do not add a named reviewer, credentials, or experience claims without verification.

### P1 — Controlled follow-on topics

After query data and human approval, evaluate these as separate informational intents:

1. How to consolidate shipments from multiple Chinese suppliers.
2. Pre-shipment inspection checklist for overseas buyers.
3. Supplier communication and production follow-up in China.
4. Shipping battery-related products from China: information required for route review.

The battery topic must not publish a universal document checklist, carrier acceptance rule, or fixed size/weight limit. Every such requirement depends on the actual product, documents, packing, origin, destination, and selected route.

### P2 — External trust references

The site has verified legal identity and a public address, but no verified official LinkedIn company page, public case studies, testimonials, memberships, or certifications. These are intentionally deferred in `memory/pending-verification.md`. Do not manufacture them to fill an SEO gap.

The off-page opportunity list prioritizes manual, permission-based entity and editorial work. It explicitly excludes automated outreach, paid link schemes, bulk directory submissions, fake reviews, and forum spam.

## What not to create

- No “best” or “cheapest sourcing agent” pages.
- No mass country pages, city pages, or templated route pages.
- No public price, transit-time, customs-clearance, inspection-result, supplier-quality, or ranking guarantees.
- No “owned warehouse” pages.
- No content based on invented clients, shipments, volumes, partner counts, certifications, or reviews.
- No separate DDU service page. DDU may remain only as a clearly labeled legacy-term explanation.
- No daily auto-published article.

## Recommended content sequence

1. Complete safe metadata and AEO clarity edits on existing pages.
2. Connect or manually export Google and Bing data; observe at least one meaningful comparison period.
3. Human-review the single freight-quote-input brief.
4. Publish at most one approved content update or draft in a weekly cycle.
5. Review impact after recrawl and sufficient data; do not react to a few days of missing rankings.

## Acceptance check for any future draft

Before publication, confirm:

- one primary intent and no collision with an existing page;
- visible direct answer before long explanation;
- verified company facts only;
- official sources for time-sensitive customs, dangerous-goods, tax, or Incoterms statements;
- no fixed route, document, price, timing, storage, insurance, refund, or acceptance rule unless separately verified;
- descriptive internal links to the relevant specialist service and Contact pages;
- a project-specific CTA;
- matching visible copy and structured data;
- human approval, build validation, and deliberate sitemap `lastmod` update.
