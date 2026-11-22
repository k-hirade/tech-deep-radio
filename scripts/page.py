"""トップページ（index.html）を組み立てる。publish.py から呼ぶ。

最新回を大きく、過去回は一覧の行で。再生は画面下の共通プレーヤー1つで行い、
聴いた位置と速度はブラウザ（localStorage）に覚えさせる。外部ファイルは読み込まない。
"""
import html
import json
import re

CSS = """
:root{--bg:#f6f4ef;--surface:#fff;--ink:#16223a;--sub:#5d6678;--faint:#8a92a3;--line:#e6e2d8;--accent:#c47f0a;--accent-ink:#fff;--accent-soft:#fbf1dc;--bar:#16223a;--bar-ink:#f3f5f9;--bar-sub:#aab4c6}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0f1622;--surface:#172133;--ink:#e9edf4;--sub:#a3adc0;--faint:#7c8699;--line:#26324a;--accent:#f2b23a;--accent-ink:#16223a;--accent-soft:#2a2a22;--bar:#1d2940;--bar-ink:#f3f5f9;--bar-sub:#9aa6bb}}
:root[data-theme="dark"]{--bg:#0f1622;--surface:#172133;--ink:#e9edf4;--sub:#a3adc0;--faint:#7c8699;--line:#26324a;--accent:#f2b23a;--accent-ink:#16223a;--accent-soft:#2a2a22;--bar:#1d2940;--bar-ink:#f3f5f9;--bar-sub:#9aa6bb}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.7 "Hiragino Sans","Noto Sans JP","Yu Gothic UI",system-ui,sans-serif;padding-bottom:160px}
button{font:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer}
a{color:var(--accent)}
.wrap{max-width:720px;margin:0 auto;padding:0 16px}
.top{display:flex;align-items:center;gap:12px;padding:20px 0 8px}
.top img{width:44px;height:44px;border-radius:10px}
.top h1{font-size:18px;margin:0;line-height:1.3}
.top p{margin:0;font-size:13px;color:var(--sub);line-height:1.5}
.label{font-size:12px;font-weight:700;letter-spacing:.08em;color:var(--accent);margin:0 0 6px}
.meta{font-size:13px;color:var(--faint);font-variant-numeric:tabular-nums}
.num{font-weight:700;color:var(--sub);margin-right:6px}
.hero{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:22px 20px;margin:16px 0 28px}
.hero h2{font-size:24px;line-height:1.4;margin:4px 0 10px;word-break:auto-phrase;text-wrap:pretty}
.hero .actions{display:flex;align-items:center;gap:14px;margin:14px 0 12px;flex-wrap:wrap}
.big-play{display:inline-flex;align-items:center;gap:10px;background:var(--accent);color:var(--accent-ink);font-weight:700;border-radius:999px;padding:12px 22px 12px 16px;font-size:16px}
.big-play svg{width:22px;height:22px;display:block}
.big-play .ic,.play .ic{display:grid;place-items:center}
.summary{margin:0;color:var(--ink);font-size:15px;line-height:1.85}
.clamp{display:-webkit-box;-webkit-box-orient:vertical;overflow:hidden}
.hero .clamp{-webkit-line-clamp:4}
.row .clamp{-webkit-line-clamp:2}
.more{font-size:13px;font-weight:700;color:var(--accent);margin-top:6px}
.hero details,.row details{margin-top:10px;font-size:13px;color:var(--sub)}
details summary{cursor:pointer;color:var(--sub);font-weight:600;list-style:none}
details summary::-webkit-details-marker{display:none}
details summary::before{content:"＋ "}
details[open] summary::before{content:"－ "}
details p{margin:8px 0}
details h3{font-size:13px;margin:12px 0 4px;color:var(--ink)}
details ul{padding-left:18px;margin:4px 0}
details a{color:inherit;overflow-wrap:anywhere}
h2.section{font-size:15px;margin:0 0 8px;color:var(--sub)}
.list{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:4px 0}
.row{display:grid;grid-template-columns:44px 1fr;gap:14px;padding:16px 18px;border-top:1px solid var(--line)}
.row:first-child{border-top:0}
.row h3{font-size:16px;line-height:1.5;margin:0 0 2px;word-break:auto-phrase;text-wrap:pretty}
.row .summary{font-size:14px;color:var(--sub);margin-top:6px}
.play{width:44px;height:44px;border-radius:50%;background:var(--accent-soft);color:var(--accent);display:grid;place-items:center}
.play svg{width:18px;height:18px;display:block;margin-left:2px}
.play[aria-pressed="true"]{background:var(--accent);color:var(--accent-ink)}
.state{font-size:12px;font-weight:700;color:var(--accent);margin-left:8px}
.state.done{color:var(--faint)}
.progress{height:3px;background:var(--line);border-radius:2px;margin-top:8px;overflow:hidden}
.progress i{display:block;height:100%;background:var(--accent)}
footer{font-size:12px;color:var(--faint);padding:28px 0 8px;line-height:1.8}
footer a{color:inherit}
.bar{position:fixed;left:0;right:0;bottom:0;background:var(--bar);color:var(--bar-ink);padding:10px 16px calc(10px + env(safe-area-inset-bottom));box-shadow:0 -6px 24px rgba(0,0,0,.18);transform:translateY(110%);transition:transform .25s}
.bar.on{transform:none}
.bar.instant{transition:none}
.bar .in{max-width:720px;margin:0 auto}
.bar .title{font-size:13px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar .ctl{display:flex;align-items:center;gap:6px;margin-top:4px}
.bar .ctl button{width:40px;height:40px;display:grid;place-items:center;border-radius:50%}
.bar .ctl button svg{width:22px;height:22px;display:block}
.bar .ctl .main{width:46px;height:46px;background:var(--accent);color:var(--accent-ink)}
.bar .ctl .speed{width:auto;min-width:52px;padding:0 10px;border:1px solid rgba(255,255,255,.25);border-radius:999px;height:32px;font-size:13px;font-weight:700;font-variant-numeric:tabular-nums}
.bar .time{font-size:12px;color:var(--bar-sub);font-variant-numeric:tabular-nums;min-width:42px;text-align:center}
.bar .seekrow{flex:1;min-width:0;display:flex;align-items:center;gap:6px}
.bar input[type=range]{flex:1;min-width:0;accent-color:var(--accent);height:24px}
@media (max-width:520px){.hero{padding:18px 16px}.hero h2{font-size:21px}.row{padding:14px 14px;gap:12px}.bar .ctl{flex-wrap:wrap;justify-content:center;gap:4px 14px}.bar .seekrow{order:-1;flex:1 0 100%}.bar .title{text-align:center}}
"""

ICON = {
    "play": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.5v13a1 1 0 0 0 1.5.86l10.6-6.5a1 1 0 0 0 0-1.72L9.5 4.64A1 1 0 0 0 8 5.5z"/></svg>',
    "pause": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>',
    "back": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 12a8 8 0 1 0 2.4-5.7"/><path d="M4 4v4h4"/><text x="12" y="15.5" font-size="7" text-anchor="middle" fill="currentColor" stroke="none" font-family="system-ui" font-weight="700">15</text></svg>',
    "fwd": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M20 12a8 8 0 1 1-2.4-5.7"/><path d="M20 4v4h-4"/><text x="12" y="15.5" font-size="7" text-anchor="middle" fill="currentColor" stroke="none" font-family="system-ui" font-weight="700">30</text></svg>',
}

JS = r"""
(() => {
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const store = {
  get(k) { try { return localStorage.getItem(k); } catch (_) { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch (_) {} },
  del(k) { try { localStorage.removeItem(k); } catch (_) {} },
};
const EPS = JSON.parse($("#eps").textContent);
const byId = Object.fromEntries(EPS.map(e => [e.id, e]));
const audio = new Audio();
audio.preload = "none";
const SPEEDS = [1, 1.25, 1.5, 1.75, 2];
let cur = null, lastSave = 0;
const fmt = s => { s = Math.max(0, Math.floor(s || 0)); const h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), x = s % 60;
  return (h ? h + ":" + String(m).padStart(2, "0") : m) + ":" + String(x).padStart(2, "0"); };
const ICON = JSON.parse($("#icons").textContent);

function speed() { const v = parseFloat(store.get("speed")); return SPEEDS.includes(v) ? v : 1; }
function showSpeed() { $("#speed").textContent = speed() + "×"; }

function refreshState(id) {
  const e = byId[id], pos = parseFloat(store.get("pos:" + id)) || 0, done = store.get("done:" + id);
  $$(`[data-state="${id}"]`).forEach(el => {
    el.textContent = done ? "聴いた" : pos > 5 ? "続き " + fmt(pos) : "";
    el.classList.toggle("done", !!done);
  });
  $$(`[data-progress="${id}"]`).forEach(el => {
    el.hidden = !(pos > 5 && !done);
    el.firstElementChild.style.width = Math.min(100, pos / e.dur * 100) + "%";
  });
}

function setButtons() {
  const playing = !audio.paused;
  $$("[data-play]").forEach(b => {
    const on = b.dataset.play === cur && playing;
    b.setAttribute("aria-pressed", on);
    b.querySelector(".ic").innerHTML = on ? ICON.pause : ICON.play;
    const lbl = b.querySelector(".lbl");
    if (lbl) lbl.textContent = on ? "一時停止" : (store.get("pos:" + b.dataset.play) > 5 ? "続きから再生" : "再生する");
  });
  $("#toggle").innerHTML = playing ? ICON.pause : ICON.play;
  $("#toggle").setAttribute("aria-label", playing ? "一時停止" : "再生");
}

function load(id) {
  const e = byId[id];
  cur = id;
  audio.src = e.src;
  audio.playbackRate = speed();
  const pos = parseFloat(store.get("pos:" + id)) || 0;
  audio.addEventListener("loadedmetadata", () => { if (pos > 5 && pos < e.dur - 10) audio.currentTime = pos; }, { once: true });
  $("#bar-title").textContent = e.title;
  $("#bar").classList.add("on");
  if ("mediaSession" in navigator) {
    navigator.mediaSession.metadata = new MediaMetadata({ title: e.title, artist: "ふかぼりテックラジオ",
      artwork: [{ src: "cover.jpg", sizes: "1400x1400", type: "image/jpeg" }] });
  }
}

function toggle(id) {
  if (id && id !== cur) { load(id); audio.play(); return; }
  if (!cur) return;
  audio.paused ? audio.play() : audio.pause();
}

function save(force) {
  if (!cur) return;
  const now = Date.now();
  if (!force && now - lastSave < 3000) return;
  lastSave = now;
  store.set("pos:" + cur, audio.currentTime.toFixed(1));
  store.set("last", cur);
  refreshState(cur);
}

$$("[data-play]").forEach(b => b.addEventListener("click", () => toggle(b.dataset.play)));
$("#toggle").addEventListener("click", () => toggle());
$("#back").addEventListener("click", () => { audio.currentTime = Math.max(0, audio.currentTime - 15); });
$("#fwd").addEventListener("click", () => { audio.currentTime = Math.min(audio.duration || 1e9, audio.currentTime + 30); });
$("#speed").addEventListener("click", () => {
  const next = SPEEDS[(SPEEDS.indexOf(speed()) + 1) % SPEEDS.length];
  store.set("speed", next); audio.playbackRate = next; showSpeed();
});
const seek = $("#seek");
let seeking = false;
seek.addEventListener("input", () => { seeking = true; $("#now").textContent = fmt(seek.value); });
seek.addEventListener("change", () => { audio.currentTime = +seek.value; seeking = false; });

audio.addEventListener("timeupdate", () => {
  const d = audio.duration || byId[cur].dur;
  seek.max = Math.floor(d);
  if (!seeking) { seek.value = Math.floor(audio.currentTime); $("#now").textContent = fmt(audio.currentTime); }
  $("#dur").textContent = fmt(d);
  save(false);
});
audio.addEventListener("play", setButtons);
audio.addEventListener("pause", () => { save(true); setButtons(); });
audio.addEventListener("ended", () => { store.set("done:" + cur, "1"); store.del("pos:" + cur); refreshState(cur); setButtons(); });
window.addEventListener("pagehide", () => save(true));

if ("mediaSession" in navigator) {
  const ms = navigator.mediaSession;
  ms.setActionHandler("play", () => audio.play());
  ms.setActionHandler("pause", () => audio.pause());
  ms.setActionHandler("seekbackward", () => $("#back").click());
  ms.setActionHandler("seekforward", () => $("#fwd").click());
}

$$(".more").forEach(b => b.addEventListener("click", () => {
  const p = b.previousElementSibling, open = p.classList.toggle("clamp");
  b.textContent = open ? "続きを読む" : "閉じる";
}));
$$(".more").forEach(b => { const p = b.previousElementSibling; if (p.scrollHeight <= p.clientHeight + 2) b.hidden = true; });

EPS.forEach(e => refreshState(e.id));
showSpeed();
const last = store.get("last");
if (last && byId[last] && !store.get("done:" + last) && store.get("pos:" + last) > 5) {
  $("#bar").classList.add("instant");
  load(last);
  requestAnimationFrame(() => requestAnimationFrame(() => $("#bar").classList.remove("instant")));
  $("#now").textContent = fmt(store.get("pos:" + last)); $("#dur").textContent = fmt(byId[last].dur);
  seek.max = byId[last].dur; seek.value = Math.floor(store.get("pos:" + last));
}
setButtons();
})();
"""


def split_title(title):
    m = re.match(r"#(\d+)\s*(.*)", title)
    return (m.group(1), m.group(2)) if m else ("", title)


def build_index(cfg, eps, md_to_html, duration):
    """eps は古い順。md_to_html / duration は publish.py のものを受け取る。"""
    base = cfg["base_url"].rstrip("/")
    e = html.escape
    data, blocks = [], []
    for i, ep in enumerate(reversed(eps)):
        sec = duration(ep["mp3"])
        num, title = split_title(ep["title"])
        body = md_to_html(ep["notes"])
        lead, _, rest = body.partition("\n")
        lead = re.sub(r"^<p>|</p>$", "", lead)
        data.append({"id": ep["id"], "src": f"{base}/{ep['key']}", "title": ep["title"], "dur": sec})
        meta = f'{ep["date"].replace("-", ".")} ・ {sec // 60}分<span class="state" data-state="{ep["id"]}"></span>'
        progress = f'<div class="progress" data-progress="{ep["id"]}" hidden><i></i></div>'
        details = f'<details><summary>注記・出典・クレジット</summary>{rest}</details>'
        if i == 0:
            blocks.append(f"""<section class="hero" aria-labelledby="latest">
  <p class="label">最新回{f" ・ #{num}" if num else ""}</p>
  <h2 id="latest">{e(title)}</h2>
  <div class="meta">{meta}</div>
  <div class="actions"><button type="button" class="big-play" data-play="{ep["id"]}"><span class="ic"></span><span class="lbl">再生する</span></button></div>
  {progress}
  <p class="summary clamp">{lead}</p><button type="button" class="more">続きを読む</button>
  {details}
</section>
<h2 class="section">これまでの回</h2>
<div class="list">""")
        else:
            blocks.append(f"""<article class="row">
  <button type="button" class="play" data-play="{ep["id"]}" aria-label="{e(ep["title"])} を再生"><span class="ic"></span></button>
  <div>
    <h3><span class="num">#{num}</span>{e(title)}</h3>
    <div class="meta">{meta}</div>
    {progress}
    <p class="summary clamp">{lead}</p><button type="button" class="more">続きを読む</button>
    {details}
  </div>
</article>""")
    if len(eps) > 1:
        blocks.append("</div>")
    elif blocks:
        blocks[0] = blocks[0].replace('<h2 class="section">これまでの回</h2>\n<div class="list">', "")
    eps_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    icons_json = json.dumps(ICON).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="ja"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(cfg["title"])}</title>
<meta name="description" content="{e(cfg["description"])}">
<meta name="theme-color" content="#16223a">
<link rel="canonical" href="{base}/"><meta property="og:url" content="{base}/">
<link rel="alternate" type="application/rss+xml" title="{e(cfg["title"])}" href="{base}/feed.xml">
<link rel="icon" href="{base}/cover.jpg"><link rel="apple-touch-icon" href="{base}/cover.jpg">
<meta property="og:title" content="{e(cfg["title"])}"><meta property="og:description" content="{e(cfg["description"])}">
<meta property="og:image" content="{base}/cover.jpg">
<style>{CSS}</style>
</head><body>
<div class="wrap">
<header class="top"><img src="{base}/cover.jpg" alt=""><div><h1>{e(cfg["title"])}</h1><p>技術ひとつを、2人の掛け合いで約40分。毎朝更新。</p></div></header>
<main>
{chr(10).join(blocks)}
</main>
<footer>{e(cfg["description"])}<br>音声合成: AivisSpeech ・ <a href="{base}/feed.xml">RSS</a></footer>
</div>
<div class="bar" id="bar" role="region" aria-label="プレーヤー"><div class="in">
  <div class="title" id="bar-title"></div>
  <div class="ctl">
    <button type="button" class="skip" id="back" aria-label="15秒戻る">{ICON["back"]}</button>
    <button type="button" class="main" id="toggle" aria-label="再生"></button>
    <button type="button" class="skip" id="fwd" aria-label="30秒進む">{ICON["fwd"]}</button>
    <div class="seekrow"><span class="time" id="now">0:00</span>
    <input type="range" id="seek" min="0" max="1" value="0" step="1" aria-label="再生位置">
    <span class="time" id="dur">0:00</span></div>
    <button type="button" class="speed" id="speed" aria-label="再生速度">1×</button>
  </div>
</div></div>
<script type="application/json" id="eps">{eps_json}</script>
<script type="application/json" id="icons">{icons_json}</script>
<script>{JS}</script>
</body></html>
"""
