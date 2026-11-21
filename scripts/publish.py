#!/usr/bin/env python3
"""R2 に公開する: 未アップロードの mp3 → カバー画像 → feed.xml（RSS）。

R2 のバケットは podcast.hiradekeishi.com で公開している。中身:
  feed.xml / cover.jpg / episodes/<日付>.mp3
アップロード済みの mp3 は .publish-state.json に記録し、二度は上げない。
"""
import argparse
import datetime
import email.utils
import glob
import html
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
        date = os.path.basename(ep_dir)
        with open(notes, encoding="utf-8") as f:
            text = f.read()
        title = text.splitlines()[0].removeprefix("# ").strip()
        title = re.sub(r"（\d{4}-\d{2}-\d{2}）$", "", title)
        eps.append({"date": date, "title": title, "notes": text, "mp3": mp3, "key": f"episodes/{date}.mp3"})
    return eps


def build_feed(cfg, eps):
    base = cfg["base_url"].rstrip("/")
    e = html.escape
    now = email.utils.format_datetime(datetime.datetime.now(JST))
    items = []
    for ep in reversed(eps):
        pub = datetime.datetime.fromisoformat(ep["date"]).replace(hour=5, tzinfo=JST)
        sec = duration(ep["mp3"])
        items.append(f"""    <item>
      <title>{e(ep["title"])}</title>
      <description><![CDATA[{md_to_html(ep["notes"])}]]></description>
      <enclosure url="{base}/{ep["key"]}" length="{os.path.getsize(ep["mp3"])}" type="audio/mpeg"/>
      <guid isPermaLink="false">fukabori-{ep["date"]}</guid>
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


def make_cover(cfg, path):
    """1400x1400 の単色カバー（番組名を文字で置くだけ）。"""
    title = cfg["title"]
    vf = (f"drawtext=fontfile={FONT}:text='{title[:4]}':fontsize=230:fontcolor=white:x=(w-tw)/2:y=h/2-260,"
          f"drawtext=fontfile={FONT}:text='{title[4:]}':fontsize=230:fontcolor=0xF5B83D:x=(w-tw)/2:y=h/2+20")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=c=0x1B2A41:s=1400x1400",
                    "-frames:v", "1", "-vf", vf, "-q:v", "3", path], check=True)


def put(cfg, key, path, content_type, cache):
    subprocess.run(["npx", "--yes", "wrangler@4", "r2", "object", "put", f"{cfg['bucket']}/{key}",
                    "--file", path, "--content-type", content_type, "--cache-control", cache, "--remote"],
                   check=True, cwd="/tmp", capture_output=True, text=True)
    print(f"uploaded {key}", flush=True)


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
    with open(STATE, "w") as f:
        json.dump(state, f, indent=1)
    print(f"{cfg['base_url']}/feed.xml")


if __name__ == "__main__":
    sys.exit(main())
