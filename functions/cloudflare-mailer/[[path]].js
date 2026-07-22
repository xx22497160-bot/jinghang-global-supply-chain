const NOT_FOUND_HEADERS = {
  "Cache-Control": "no-store",
  "Content-Type": "text/plain; charset=utf-8",
  "X-Content-Type-Options": "nosniff",
  "X-Robots-Tag": "noindex",
};

export function onRequest() {
  return new Response("Not Found", {
    status: 404,
    headers: NOT_FOUND_HEADERS,
  });
}
