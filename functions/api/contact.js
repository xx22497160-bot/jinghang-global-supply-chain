const MAX_REQUEST_BYTES = 32 * 1024;
const TURNSTILE_ACTION = "contact_enquiry";
const TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify";
const MAILER_URL = "https://contact-mailer.internal/send";

const RESPONSE_HEADERS = {
  "Cache-Control": "no-store",
  "Content-Type": "application/json; charset=utf-8",
  "X-Content-Type-Options": "nosniff",
};

const PROJECT_STAGES = new Set([
  "Looking for factories",
  "Comparing samples",
  "Preparing an order",
  "Production in progress",
  "Goods ready to ship",
  "Recurring supply chain",
]);

const SERVICES = new Set([
  "Supplier sourcing",
  "Sample coordination",
  "Procurement support",
  "Inspection coordination",
  "Consolidation",
  "International logistics",
  "DDP or DAP",
  "Special cargo",
  "Partner warehouse or fulfillment review",
]);

const FIELD_LIMITS = {
  full_name: 100,
  company_name: 160,
  work_email: 254,
  country_and_time_zone: 120,
  company_website: 500,
  project_stage: 80,
  product_and_project_details: 5000,
  supplier_quantity_and_cargo: 4000,
  origin_city: 160,
  destination: 240,
  sensitive_cargo_details: 4000,
  target_date: 10,
  messaging_contact: 200,
  website_url: 500,
  turnstile_token: 2048,
};

function respond(status, payload, extraHeaders = {}) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      ...RESPONSE_HEADERS,
      ...extraHeaders,
    },
  });
}

function cleanText(value) {
  return typeof value === "string" ? value.trim() : "";
}

function singleLine(value) {
  return cleanText(value).replace(/[\r\n\u0000-\u001f\u007f]+/g, " ").replace(/\s+/g, " ");
}

function validEmail(value) {
  return value.length <= FIELD_LIMITS.work_email
    && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
    && !/[\r\n]/.test(value);
}

function validHttpUrl(value) {
  if (!value) {
    return true;
  }

  try {
    const parsed = new URL(value);
    return parsed.protocol === "https:" || parsed.protocol === "http:";
  } catch (_error) {
    return false;
  }
}

function validatePayload(raw) {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    return { error: "Invalid form data." };
  }

  const data = {};
  for (const [field, maxLength] of Object.entries(FIELD_LIMITS)) {
    data[field] = cleanText(raw[field]);
    if (data[field].length > maxLength) {
      return { error: "One or more fields are too long." };
    }
  }

  if (data.website_url) {
    return { bot: true };
  }

  if (data.full_name.length < 2) {
    return { error: "Please provide your full name." };
  }
  if (!validEmail(data.work_email)) {
    return { error: "Please provide a valid work email." };
  }
  if (!PROJECT_STAGES.has(data.project_stage)) {
    return { error: "Please select a valid project stage." };
  }
  if (data.product_and_project_details.length < 20) {
    return { error: "Please provide at least 20 characters of project detail." };
  }
  if (!validHttpUrl(data.company_website)) {
    return { error: "Please provide a valid company website URL." };
  }
  if (data.target_date && !/^\d{4}-\d{2}-\d{2}$/.test(data.target_date)) {
    return { error: "Please provide a valid target date." };
  }
  if (raw.information_confirmation !== "confirmed") {
    return { error: "Please confirm that the enquiry information is accurate." };
  }
  if (!data.turnstile_token) {
    return { error: "Please complete the security check." };
  }

  const rawServices = Array.isArray(raw.services) ? raw.services : [];
  if (rawServices.length > SERVICES.size) {
    return { error: "Please select only the listed services." };
  }
  const services = rawServices.map(cleanText);
  if (services.some((service) => !SERVICES.has(service))) {
    return { error: "Please select only the listed services." };
  }

  return {
    data: {
      ...data,
      services: [...new Set(services)],
    },
  };
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function display(value) {
  return value || "Not provided";
}

function buildMessage(data) {
  const rows = [
    ["Full name", data.full_name],
    ["Company", data.company_name],
    ["Work email", data.work_email],
    ["Country / time zone", data.country_and_time_zone],
    ["Company website", data.company_website],
    ["Messaging contact", data.messaging_contact],
    ["Current stage", data.project_stage],
    ["Product and project details", data.product_and_project_details],
    ["Suppliers, quantity, and cargo", data.supplier_quantity_and_cargo],
    ["Origin city", data.origin_city],
    ["Destination city and postal code", data.destination],
    ["Sensitive or special cargo", data.sensitive_cargo_details],
    ["Support requested", data.services.join(", ")],
    ["Target shipment or launch date", data.target_date],
  ];

  const companyOrName = singleLine(data.company_name || data.full_name).slice(0, 100);
  const subject = `Website enquiry | ${companyOrName} | ${singleLine(data.project_stage)}`;
  const text = [
    "New project enquiry from jinghangsc.com",
    "",
    ...rows.flatMap(([label, value]) => [`${label}:`, display(value), ""]),
    "The sender confirmed that the information is accurate to the best of their knowledge.",
  ].join("\n");

  const htmlRows = rows.map(([label, value]) => (
    `<tr><th align="left" valign="top" style="padding:8px;border-bottom:1px solid #dfe7e9;">${escapeHtml(label)}</th>`
      + `<td valign="top" style="padding:8px;border-bottom:1px solid #dfe7e9;white-space:pre-wrap;">${escapeHtml(display(value))}</td></tr>`
  )).join("");
  const html = `<!doctype html><html><body style="font-family:Arial,sans-serif;color:#17242b;">`
    + `<h1 style="font-size:20px;">New project enquiry from jinghangsc.com</h1>`
    + `<table style="border-collapse:collapse;width:100%;max-width:760px;">${htmlRows}</table>`
    + `<p style="font-size:13px;color:#52636c;">The sender confirmed that the information is accurate to the best of their knowledge.</p>`
    + `</body></html>`;

  return { subject, text, html };
}

async function verifyTurnstile(request, env, token, fetchImpl) {
  const secret = cleanText(env.TURNSTILE_SECRET_KEY);
  if (!secret) {
    return { ok: false, configurationError: true };
  }

  const body = new FormData();
  body.set("secret", secret);
  body.set("response", token);
  body.set("idempotency_key", crypto.randomUUID());
  const remoteIp = request.headers.get("CF-Connecting-IP");
  if (remoteIp) {
    body.set("remoteip", remoteIp);
  }

  let verificationResponse;
  try {
    verificationResponse = await fetchImpl(TURNSTILE_VERIFY_URL, {
      method: "POST",
      body,
    });
  } catch (_error) {
    return { ok: false, unavailable: true };
  }

  if (!verificationResponse.ok) {
    return { ok: false, unavailable: true };
  }

  let result;
  try {
    result = await verificationResponse.json();
  } catch (_error) {
    return { ok: false, unavailable: true };
  }

  const requestHostname = new URL(request.url).hostname;
  const actionMatches = result.action === TURNSTILE_ACTION;
  const hostnameMatches = result.hostname === requestHostname;
  return {
    ok: result.success === true && actionMatches && hostnameMatches,
    unavailable: false,
  };
}

async function sendToMailer(env, data) {
  if (!env.CONTACT_MAILER || typeof env.CONTACT_MAILER.fetch !== "function") {
    return { ok: false, configurationError: true };
  }

  const message = buildMessage(data);
  let mailerResponse;
  try {
    mailerResponse = await env.CONTACT_MAILER.fetch(MAILER_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json; charset=utf-8",
      },
      body: JSON.stringify({
        replyTo: data.work_email,
        replyToName: data.full_name,
        ...message,
      }),
    });
  } catch (_error) {
    return { ok: false };
  }

  return { ok: mailerResponse.ok };
}

export async function handleContactRequest(context, fetchImpl = fetch) {
  const { request, env } = context;
  if (request.method !== "POST") {
    return respond(405, { ok: false, message: "Method not allowed." }, { Allow: "POST" });
  }

  const requestUrl = new URL(request.url);
  if (request.headers.get("Origin") !== requestUrl.origin) {
    return respond(403, { ok: false, message: "This request could not be accepted." });
  }

  if (!request.headers.get("Content-Type")?.toLowerCase().startsWith("application/json")) {
    return respond(415, { ok: false, message: "Unsupported request format." });
  }

  const declaredLength = Number(request.headers.get("Content-Length") || 0);
  if (declaredLength > MAX_REQUEST_BYTES) {
    return respond(413, { ok: false, message: "The enquiry is too large to submit." });
  }

  let raw;
  try {
    raw = await request.json();
  } catch (_error) {
    return respond(400, { ok: false, message: "Invalid form data." });
  }

  const encodedLength = new TextEncoder().encode(JSON.stringify(raw)).byteLength;
  if (encodedLength > MAX_REQUEST_BYTES) {
    return respond(413, { ok: false, message: "The enquiry is too large to submit." });
  }

  const validation = validatePayload(raw);
  if (validation.bot) {
    return respond(200, { ok: true, message: "Thank you. Your enquiry has been received." });
  }
  if (validation.error) {
    return respond(400, { ok: false, message: validation.error });
  }

  const turnstile = await verifyTurnstile(
    request,
    env,
    validation.data.turnstile_token,
    fetchImpl,
  );
  if (turnstile.configurationError || turnstile.unavailable) {
    return respond(503, {
      ok: false,
      message: "The security check is temporarily unavailable. Please try again or email us directly.",
    });
  }
  if (!turnstile.ok) {
    return respond(400, {
      ok: false,
      message: "The security check expired or could not be verified. Please try again.",
    });
  }

  const mailer = await sendToMailer(env, validation.data);
  if (!mailer.ok) {
    return respond(503, {
      ok: false,
      message: "We could not send the enquiry right now. Please try again or email us directly.",
    });
  }

  return respond(200, {
    ok: true,
    message: "Thank you. Your enquiry has been sent to Anna, who normally replies within 24 hours.",
  });
}

export const onRequest = handleContactRequest;
