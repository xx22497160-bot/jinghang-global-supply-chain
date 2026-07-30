# Enquiry Conversion Audit

Audit scope: the checked-in Jinghang Global Supply Chain production source. This is a source-code review, not a claim that every future form submission will be delivered.

## Current Conversion Paths

| Path | Current implementation | Verification status | Conversion implication |
|---|---|---|---|
| Project enquiry form | Same-origin `POST /api/contact` request sent as JSON by `contact.js` | Implemented in source | This is the strongest enquiry path. A successful API response is required before a form submission can be counted as successful. |
| Email | Clickable `mailto:hello@jinghangsc.com` links | Implemented in source | The website can observe a future click only if approved analytics is added. It cannot prove that the visitor sent the email. |
| WhatsApp | Clickable `https://wa.me/8615018538243` link | Implemented in source | A future click can be measured, but a completed conversation cannot be inferred from the click. |
| WeChat | No verified company WeChat contact is published | Correctly unavailable | Verify it through the project fact-control process before adding a public ID, copy control, or `wechat_copy` measurement. |
| Service CTAs | Service and editorial pages link to `/contact` | Implemented in source | CTA clicks are not currently measured. Page-specific CTA labels should remain aligned with the visitor's service intent. |

## Secure Form Review

The production source contains a real server-side enquiry flow:

- The form submits to the same-origin `/api/contact` endpoint.
- Client-side JavaScript obtains a public Turnstile site key from `/api/contact-config`.
- The Pages Function validates request origin, content type, request size, required fields, field limits, email format, allowed service values, a honeypot field, and the Turnstile token.
- Turnstile verification checks both the expected action and the request hostname.
- The validated enquiry is passed through a private `CONTACT_MAILER` service binding.
- The browser receives success only after the mailer service returns a successful response.
- Error messages provide a direct-email fallback.
- With JavaScript disabled, the page provides a direct-email fallback rather than pretending the secure form can submit.
- The source and Privacy Notice state that the site does not create a separate form-submission database.

Production delivery still depends on Cloudflare variables, encrypted secrets, service bindings, email routing, and the receiving mailbox. Those values must remain outside Git and logs.

## Friction and Gaps

1. **No approved measurement is active.** The source includes no marketing analytics or conversion-event collector. Enquiry counts, click counts, and funnel rates are therefore `未连接 (Not connected)`, not zero.
2. **WeChat is not verified.** Project memory does not contain an approved WeChat ID. Do not publish, measure, or imply a WeChat contact channel until it is verified through the project's fact-control process.
3. **The form is intentionally detailed.** The required fields are limited to name, work email, project stage, project details, confirmation, and Turnstile. Optional operational fields improve feasibility review without blocking all visitors.
4. **An email click is not an email sent.** The same distinction applies to WhatsApp clicks and completed conversations.
5. **A form start is not an enquiry.** `project_brief_start` must remain separate from `project_brief_submit`.
6. **CTA wording is partly generic.** The shared header CTA is appropriate for navigation, while core service pages should use intent-specific CTA labels. Any wording changes belong in a reviewed page optimization, not the monitoring automation.

## Approved Event Specification

No event code was added in this audit. The following names are reserved for a future, explicitly approved implementation.

| Event | Fire only when | Do not infer |
|---|---|---|
| `project_brief_start` | A visitor first focuses or changes a meaningful enquiry-form field | Intent to submit, a qualified lead, or a sent enquiry |
| `project_brief_submit` | `/api/contact` returns the documented successful response after Turnstile and mail delivery | Inbox reading, qualification, quotation, order, or revenue |
| `email_click` | A visitor activates a `mailto:hello@jinghangsc.com` link | Email sent or received |
| `whatsapp_click` | A visitor activates the verified `wa.me` link | Message sent or conversation completed |
| `wechat_copy` | A future fact-verified WeChat ID and copy control are explicitly approved, and the control successfully copies the ID | Contact added or message sent |
| `service_cta_click` | A service-context CTA is activated | Contact-page load, form start, or enquiry |

Permitted minimal fields:

- event name
- event timestamp
- current page path
- CTA identifier or service context
- coarse referrer category if approved
- success or failure state for the form endpoint, without the error body containing personal data

Prohibited analytics fields:

- name, email, phone number, WhatsApp or WeChat contact
- company name or website
- product, supplier, cargo, quantity, value, route, document, date, or project details
- Turnstile token, IP address copied into analytics, cookie identifiers, secrets, or service-binding details

## Recommended Safe Sequence

1. Keep the current no-marketing-analytics state until the owner approves a measurement option.
2. Confirm the desired retention period and who may access aggregate event reports.
3. Update the Privacy Notice and any required consent controls before enabling measurement.
4. Implement only the five currently applicable events with no form-field payload. Keep `wechat_copy` inactive until a company contact is fact-verified and approved.
5. Test in a non-production environment, then verify a real production enquiry separately.
6. Distinguish visits, event clicks, successful form submissions, mailbox delivery, qualified enquiries, quotations, and customers in every report.

## Current Decision

No analytics script, pixel, event endpoint, cookie, tracker, email, external message, deployment, or publication was added by this audit.
