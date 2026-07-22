const RESPONSE_HEADERS = {
  "Cache-Control": "no-store",
  "Content-Type": "application/json; charset=utf-8",
  "X-Content-Type-Options": "nosniff",
};

function respond(status, payload) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: RESPONSE_HEADERS,
  });
}

export async function onRequest(context) {
  if (context.request.method !== "GET") {
    return new Response(null, {
      status: 405,
      headers: {
        ...RESPONSE_HEADERS,
        Allow: "GET",
      },
    });
  }

  const siteKey = String(context.env.TURNSTILE_SITE_KEY || "").trim();
  if (!siteKey) {
    return respond(503, {
      ok: false,
      message: "The secure enquiry form is temporarily unavailable.",
    });
  }

  return respond(200, { ok: true, siteKey });
}
