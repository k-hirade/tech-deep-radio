#!/usr/bin/env python3
"""R2 に公開する: 未アップロードの mp3 → カバー画像 → feed.xml（RSS）。

R2 のバケットは podcast.hiradekeishi.com で公開している。中身:
  feed.xml / cover.jpg / episodes/<日付>.mp3
アップロード済みの mp3 は .publish-state.json に記録し、二度は上げない。
アップロードは wrangler のログインで行う。~/.config/fukabori/r2.env にバケット限定の R2 キーを
置けば（scripts/setup_credentials.sh）、そちらを使う。
"""
import argparse
import datetime
import email.utils
import glob
import hashlib
import hmac
import html
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R2_ENV = os.path.expanduser("~/.config/fukabori/r2.env")
STATE = os.path.join(ROOT, ".publish-state.json")
JST = datetime.timezone(datetime.timedelta(hours=9))
FONT = os.path.expanduser("~/Library/Fonts/NotoSansCJKjp-Bold.otf")


def load_config():
    with open(os.path.join(ROOT, "config", "podcast.json"), encoding="utf-8") as f:
        return json.load(f)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         check=True, capture_output=True, text=True).stdout
    return int(float(out))


def md_to_html(text):
    """notes.md（見出し・段落・箇条書き・URL だけ）を概要欄用の HTML にする。"""
    out, items = [], []

    def flush():
        if items:
            out.append("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")
            items.clear()

    def inline(s):
        s = html.escape(s)
        return re.sub(r"(https?://[^\s<)）]+)", r'<a href="\1">\1</a>', s)

    for line in text.splitlines()[1:]:  # 1行目は題名
        s = line.strip()
        if s.startswith("- "):
            items.append(inline(s[2:]))
            continue
        flush()
        if s.startswith("## "):
            out.append(f"<h3>{inline(s[3:])}</h3>")
        elif s:
            out.append(f"<p>{inline(s)}</p>")
    flush()
    return "\n".join(out)


def episodes():
    eps = []
    for notes in sorted(glob.glob(os.path.join(ROOT, "episodes", "*", "notes.md"))):
        ep_dir = os.path.dirname(notes)
        mp3 = os.path.join(ep_dir, "episode.mp3")
        if not os.path.exists(mp3):
            continue
        ep_id = os.path.basename(ep_dir)  # 2026-11-22 / 同じ日の2本目は 2026-11-22-2
        date = ep_id[:10]
        slot = int(ep_id[11:] or 1)
        with open(notes, encoding="utf-8") as f:
            text = f.read()
        title = text.splitlines()[0].removeprefix("# ").strip()
        title = re.sub(r"（\d{4}-\d{2}-\d{2}）$", "", title)
        eps.append({"id": ep_id, "date": date, "slot": slot, "title": title, "notes": text, "mp3": mp3,
                    "key": f"episodes/{ep_id}.mp3"})
    return eps


def build_feed(cfg, eps):
    base = cfg["base_url"].rstrip("/")
    e = html.escape
    now = email.utils.format_datetime(datetime.datetime.now(JST))
    items = []
    for ep in reversed(eps):
        pub = datetime.datetime.fromisoformat(ep["date"]).replace(hour=4 + ep["slot"], tzinfo=JST)  # 2本目は6時、3本目は7時
        sec = duration(ep["mp3"])
        items.append(f"""    <item>
      <title>{e(ep["title"])}</title>
      <description><![CDATA[{md_to_html(ep["notes"]).replace("]]>", "]]&gt;")}]]></description>
      <enclosure url="{base}/{ep["key"]}" length="{os.path.getsize(ep["mp3"])}" type="audio/mpeg"/>
      <guid isPermaLink="false">fukabori-{ep["id"]}</guid>
      <pubDate>{email.utils.format_datetime(pub)}</pubDate>
      <itunes:duration>{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
      <itunes:episodeType>full</itunes:episodeType>
    </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{e(cfg["title"])}</title>
    <link>{base}/</link>
    <atom:link href="{base}/feed.xml" rel="self" type="application/rss+xml"/>
    <description>{e(cfg["description"])}</description>
    <language>{cfg["language"]}</language>
    <lastBuildDate>{now}</lastBuildDate>
    <itunes:author>{e(cfg["author"])}</itunes:author>
    <itunes:image href="{base}/cover.jpg"/>
    <itunes:category text="{e(cfg["category"])}"/>
    <itunes:explicit>false</itunes:explicit>
    <itunes:type>episodic</itunes:type>
{chr(10).join(items)}
  </channel>
</rss>
"""


PAGE_CSS = """
:root{--bg:#f7f5f0;--card:#fff;--ink:#1b2a41;--sub:#5b6475;--line:#e4e0d6;--accent:#c98a12;--chip:#f1ece0}
@media (prefers-color-scheme:dark){:root{--bg:#121a26;--card:#1b2536;--ink:#e8ecf2;--sub:#9aa5b8;--line:#2b3850;--accent:#f5b83d;--chip:#243049}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.75 "Hiragino Sans","Noto Sans JP","Yu Gothic UI",system-ui,sans-serif}
main{max-width:760px;margin:0 auto;padding:32px 16px 64px}
header{display:flex;gap:20px;align-items:center;margin-bottom:24px}
header img{width:120px;height:120px;border-radius:14px;flex:none}
h1{font-size:28px;line-height:1.3;margin:0 0 6px}
.lead{color:var(--sub);margin:0;font-size:15px}
.subscribe{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin-bottom:32px}
.subscribe h2{font-size:15px;margin:0 0 8px}
.feed{display:flex;gap:8px;flex-wrap:wrap}
.feed code{flex:1 1 260px;background:var(--chip);border-radius:8px;padding:8px 10px;font-size:14px;overflow-wrap:anywhere}
.feed button{border:0;border-radius:8px;padding:8px 14px;background:var(--accent);color:#1b2a41;font-weight:700;cursor:pointer}
.subscribe p{margin:8px 0 0;font-size:13px;color:var(--sub)}
article{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;margin-bottom:16px}
.meta{font-size:13px;color:var(--sub)}
article h3{font-size:19px;line-height:1.45;margin:2px 0 10px}
audio{width:100%;margin:4px 0 8px}
article p{margin:0 0 8px;font-size:15px}
details{font-size:14px;color:var(--sub)}
details summary{cursor:pointer;color:var(--accent);font-weight:600}
details h3{font-size:14px;margin:12px 0 4px;color:var(--ink)}
details ul{padding-left:20px;margin:4px 0}
details a{color:inherit;overflow-wrap:anywhere}
footer{margin-top:32px;font-size:13px;color:var(--sub)}
@media (max-width:520px){header{flex-direction:column;align-items:flex-start}header img{width:96px;height:96px}h1{font-size:24px}}
"""


def build_index(cfg, eps):
    base = cfg["base_url"].rstrip("/")
    e = html.escape
    cards = []
    for ep in reversed(eps):
        sec = duration(ep["mp3"])
        body = md_to_html(ep["notes"])
        lead, _, rest = body.partition("\n")
        cards.append(f"""<article>
  <div class="meta">{ep["date"]} ・ {sec // 60}分</div>
  <h3>{e(ep["title"])}</h3>
  <audio controls preload="none" src="{base}/{ep["key"]}"></audio>
  {lead}
  <details><summary>注記・出典・クレジット</summary>{rest}</details>
</article>""")
    return f"""<!doctype html>
<html lang="ja"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(cfg["title"])}</title>
<meta name="description" content="{e(cfg["description"])}">
<link rel="alternate" type="application/rss+xml" title="{e(cfg["title"])}" href="{base}/feed.xml">
<link rel="icon" href="{base}/cover.jpg">
<meta property="og:title" content="{e(cfg["title"])}"><meta property="og:image" content="{base}/cover.jpg">
<style>{PAGE_CSS}</style>
</head><body><main>
<header><img src="{base}/cover.jpg" alt=""><div><h1>{e(cfg["title"])}</h1><p class="lead">{e(cfg["description"])}</p></div></header>
<section class="subscribe"><h2>ポッドキャストアプリで購読</h2>
<div class="feed"><code id="feed">{base}/feed.xml</code><button type="button" id="copy">コピー</button></div>
<p>Apple Podcasts は「ライブラリ → … → URLで番組をフォロー」、Overcast や Pocket Casts は「URLを追加」に貼り付けてください。</p></section>
{chr(10).join(cards)}
<footer>音声合成: AivisSpeech ・ 台本は AI（Claude）の支援で作成しています。</footer>
</main>
<script>
document.getElementById("copy").onclick=async e=>{{try{{await navigator.clipboard.writeText(document.getElementById("feed").textContent);e.target.textContent="コピーしました"}}catch(_){{}}}};
</script>
</body></html>
"""


def make_cover(cfg, path):
    """1400x1400 の単色カバー（番組名を文字で置くだけ）。"""
    title = cfg["title"]
    vf = (f"drawtext=fontfile={FONT}:text='{title[:4]}':fontsize=230:fontcolor=white:x=(w-tw)/2:y=h/2-260,"
          f"drawtext=fontfile={FONT}:text='{title[4:]}':fontsize=230:fontcolor=0xF5B83D:x=(w-tw)/2:y=h/2+20")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=c=0x1B2A41:s=1400x1400",
                    "-frames:v", "1", "-vf", vf, "-q:v", "3", path], check=True)


def r2_credentials():
    """~/.config/fukabori/r2.env（このバケットだけ読み書きできる R2 の API トークン）を読む。"""
    creds = {}
    with open(R2_ENV) as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                creds[k] = v
    missing = {"R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY"} - creds.keys()
    if missing:
        sys.exit(f"{R2_ENV} に {', '.join(sorted(missing))} がない（scripts/setup_credentials.sh で設定）")
    return creds


def has_r2_keys():
    try:
        with open(R2_ENV) as f:
            return "R2_SECRET_ACCESS_KEY=" in f.read()
    except OSError:
        return False


def put(cfg, key, path, content_type, cache):
    """R2 のキー（r2.env）があれば S3 互換 API で、なければ wrangler のログインで上げる。"""
    if has_r2_keys():
        put_s3(cfg, key, path, content_type, cache)
    else:
        subprocess.run(["npx", "--yes", "wrangler@4", "r2", "object", "put", f"{cfg['bucket']}/{key}",
                        "--file", path, "--content-type", content_type, "--cache-control", cache, "--remote"],
                       check=True, cwd="/tmp", capture_output=True, text=True)
    print(f"uploaded {key}", flush=True)


def put_s3(cfg, key, path, content_type, cache):
    """R2 の S3 互換 API に PUT する（AWS 署名 V4、標準ライブラリだけ）。"""
    c = r2_credentials()
    host = f"{c['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com"
    uri = "/" + urllib.parse.quote(f"{cfg['bucket']}/{key}")
    with open(path, "rb") as f:
        body = f.read()
    now = datetime.datetime.now(datetime.timezone.utc)
    amz_date, day = now.strftime("%Y%m%dT%H%M%SZ"), now.strftime("%Y%m%d")
    payload_hash = hashlib.sha256(body).hexdigest()
    headers = {"cache-control": cache, "content-type": content_type, "host": host,
               "x-amz-content-sha256": payload_hash, "x-amz-date": amz_date}
    signed = ";".join(sorted(headers))
    canonical = "\n".join(["PUT", uri, "", "".join(f"{k}:{headers[k]}\n" for k in sorted(headers)), signed, payload_hash])
    scope = f"{day}/auto/s3/aws4_request"
    to_sign = "\n".join(["AWS4-HMAC-SHA256", amz_date, scope, hashlib.sha256(canonical.encode()).hexdigest()])
    k = ("AWS4" + c["R2_SECRET_ACCESS_KEY"]).encode()
    for part in (day, "auto", "s3", "aws4_request"):
        k = hmac.new(k, part.encode(), hashlib.sha256).digest()
    sig = hmac.new(k, to_sign.encode(), hashlib.sha256).hexdigest()
    headers["authorization"] = (f"AWS4-HMAC-SHA256 Credential={c['R2_ACCESS_KEY_ID']}/{scope}, "
                                f"SignedHeaders={signed}, Signature={sig}")
    del headers["host"]
    req = urllib.request.Request(f"https://{host}{uri}", data=body, method="PUT", headers=headers)
    try:
        urllib.request.urlopen(req, timeout=300).read()
    except urllib.error.HTTPError as e:
        sys.exit(f"R2 へのアップロード失敗 {key}: {e.code} {e.read()[:300]!r}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="feed.xml とカバーを作るだけで上げない")
    args = ap.parse_args()
    cfg = load_config()
    eps = episodes()
    out_dir = os.path.join(ROOT, "work")
    os.makedirs(out_dir, exist_ok=True)

    feed = os.path.join(out_dir, "feed.xml")
    with open(feed, "w", encoding="utf-8") as f:
        f.write(build_feed(cfg, eps))
    index = os.path.join(out_dir, "index.html")
    with open(index, "w", encoding="utf-8") as f:
        f.write(build_index(cfg, eps))
    cover = os.path.join(out_dir, "cover.jpg")
    if not os.path.exists(cover):
        make_cover(cfg, cover)
    print(f"{len(eps)} episodes → {feed}")
    if args.dry_run:
        return

    state = {}
    if os.path.exists(STATE):
        with open(STATE) as f:
            state = json.load(f)
    for ep in eps:
        stamp = f"{os.path.getsize(ep['mp3'])}:{int(os.path.getmtime(ep['mp3']))}"
        if state.get(ep["key"]) != stamp:
            put(cfg, ep["key"], ep["mp3"], "audio/mpeg", "public, max-age=86400")
            state[ep["key"]] = stamp
            with open(STATE, "w") as f:
                json.dump(state, f, indent=1)
    if not state.get("cover.jpg"):
        put(cfg, "cover.jpg", cover, "image/jpeg", "public, max-age=86400")
        state["cover.jpg"] = True
    put(cfg, "feed.xml", feed, "application/rss+xml; charset=utf-8", "public, max-age=300")
    put(cfg, "index.html", index, "text/html; charset=utf-8", "public, max-age=300")
    with open(STATE, "w") as f:
        json.dump(state, f, indent=1)
    print(f"{cfg['base_url']}/feed.xml")


if __name__ == "__main__":
    sys.exit(main())
