// /（?… 付きも）は R2 の index.html を返し、/index.html は / に転送する。それ以外は R2 のカスタムドメインへ素通し。
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/index.html") {
      url.pathname = "/";
      return Response.redirect(url.toString(), 301);
    }
    if (url.pathname !== "/") return fetch(request);
    if (!["GET", "HEAD"].includes(request.method)) return new Response("Method Not Allowed", { status: 405 });
    const obj = await env.BUCKET.get("index.html");
    if (!obj) return new Response("Not Found", { status: 404 });
    const headers = new Headers();
    obj.writeHttpMetadata(headers);
    headers.set("etag", obj.httpEtag);
    return new Response(request.method === "HEAD" ? null : obj.body, { headers });
  },
};
