#!/usr/bin/env python3
"""毎朝の1回分を作る: 台本を Claude に書かせる → 書式を確かめる → 音声合成 → コミットして push → 公開。

途中で止まっても、もう一度実行すれば続きから進む（台本があれば書かせない、合成済みの発言は作り直さない）。

回の ID はフォルダ名で、ふつうは日付（2026-11-22）。同じ日の2本目以降は 2026-11-22-2 のように番号を付ける。
テーマの指定: requests/<ID>.md（なければ requests/<日付>.md）があれば、話題選びをせずそのテーマで作る。
"""
import argparse
import datetime
import fcntl
import glob
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.environ.get("AIVIS_ENGINE", "http://localhost:10101")
MODEL = os.environ.get("FUKABORI_MODEL", "opus")
MIN_CHARS, MAX_CHARS = 10000, 20000  # これを外れたら失敗扱い（目安は1.5万〜1.6万字）
TARGET_CHARS = 14500  # これに届かなければ加筆させる
EXPAND_TRIES = 2
LINE = re.compile(r"^[TY]\|\S")
EP_ID = re.compile(r"^\d{4}-\d{2}-\d{2}(-[2-9])?$")

THEME_SECTION = """

## テーマの指定（最優先）
この回のテーマは、番組の持ち主から次のとおり指定されています。手順1の話題選びは行わず、このテーマで作ってください。
ここ数日の関連ニュースや動きがあれば「なぜ今この話か」に使い、なければ無理に作らず、テーマそのものの面白さから入ってください。
過去回と重なる部分は避けてください。

> {theme}
"""


def log(msg):
    print(f"[{datetime.datetime.now():%H:%M:%S}] {msg}", flush=True)


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=ROOT, check=check, text=True, capture_output=True)


def episode_number(ep):
    done = [d for d in glob.glob(os.path.join(ROOT, "episodes", "*", "notes.md"))
            if os.path.basename(os.path.dirname(d)) < ep]
    return len(done) + 1


def theme_request(ep):
    """requests/<ID>.md、なければ requests/<日付>.md の中身（テーマ指定）を返す。"""
    for name in dict.fromkeys([ep, ep[:10]]):
        path = os.path.join(ROOT, "requests", f"{name}.md")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                text = f.read().strip()
            if text:
                return path, text
    return None, None


def run_claude(ep, prompt, label):
    # Edit(パス) は Write にも効く。Write(パス) の形は効かない（試して確認済み）
    os.makedirs(os.path.join(ROOT, ".research", ep), exist_ok=True)
    tools = ["Read", "Glob", "Grep", "WebSearch", "WebFetch", "Bash(python3 scripts/count_chars.py:*)",
             f"Edit(./episodes/{ep}/**)", f"Edit(./.research/{ep}/**)", "Edit(./config/readings.json)"]
    cmd = ["claude", "-p", "--model", MODEL, "--permission-mode", "dontAsk", "--setting-sources", "project",
           "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
           "--output-format", "json", "--no-session-persistence", "--allowedTools", *tools]
    log(f"{label}（model={MODEL}）")
    p = subprocess.run(cmd, input=prompt, text=True, cwd=ROOT, capture_output=True, timeout=3 * 3600)
    try:
        d = json.loads(p.stdout)
    except ValueError:
        sys.exit(f"claude の出力を読めない exit={p.returncode} {p.stderr[:500]}")
    log(f"claude: turns={d.get('num_turns')} cost=${d.get('total_cost_usd')} → {str(d.get('result'))[-300:]}")
    if d.get("is_error"):
        sys.exit("claude がエラーで終了")


def generate(ep, number):
    with open(os.path.join(ROOT, "prompts", "daily.md"), encoding="utf-8") as f:
        prompt = f.read().format(date=ep[:10], ep=ep, number=number)
    path, theme = theme_request(ep)
    if theme:
        log(f"テーマ指定あり: {os.path.relpath(path, ROOT)}")
        prompt += THEME_SECTION.replace("{theme}", theme.replace("\n", "\n> "))
    run_claude(ep, prompt, "台本を生成")


def expand(ep, chars):
    prompt = (f"`episodes/{ep}/` の台本が {chars} 字で、目標の {TARGET_CHARS}〜16000 字に足りません。"
              f"`docs/format.md` を守り、話の流れと各章の核心を保ったまま、足りない分を加筆してください。"
              f"薄い章に、たとえ話・ユウが自分で考える場面・歴史・落とし穴を足すのが目安です。"
              f"新しい発言は既存の script_*.txt に差し込み、ファイルを増やさないこと。"
              f"字数は `python3 scripts/count_chars.py episodes/{ep}` で確かめられます。"
              f"新しく入れる事実（年・数字・人名）は WebSearch / WebFetch で確かめ、出典を足したら notes.md にも追記。"
              f"音声は呼び出し側が作り直す。git の操作はしない。最後に加筆後の字数を1行で報告。")
    run_claude(ep, prompt, f"加筆（{chars}字）")


def validate(ep_dir):
    files = sorted(glob.glob(os.path.join(ep_dir, "script_*.txt")))
    if not files:
        sys.exit("台本がない")
    chars, errors = 0, []
    for path in files:
        with open(path, encoding="utf-8") as f:
            for n, raw in enumerate(f, 1):
                s = raw.strip()
                if not s:
                    continue
                if not LINE.match(s):
                    errors.append(f"{os.path.basename(path)}:{n}: {s[:40]}")
                chars += len(s) - 2
    if errors:
        sys.exit("書式違反:\n" + "\n".join(errors[:20]))
    if not MIN_CHARS <= chars <= MAX_CHARS:
        sys.exit(f"字数が範囲外: {chars}")
    if not os.path.exists(os.path.join(ep_dir, "notes.md")):
        sys.exit("notes.md がない")
    with open(os.path.join(ROOT, "config", "readings.json"), encoding="utf-8") as f:
        json.load(f)
    log(f"書式OK: {len(files)}ファイル {chars}字")
    return chars


def wait_engine(seconds=300):
    for _ in range(seconds):
        try:
            urllib.request.urlopen(f"{ENGINE}/version", timeout=2)
            return
        except OSError:
            time.sleep(1)
    sys.exit("AivisSpeech Engine に繋がらない（systemctl --user status aivisspeech）")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", dest="ep", default=datetime.date.today().isoformat(),
                    help="回の ID。ふつうは日付、同じ日の2本目は 2026-11-22-2")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--no-publish", action="store_true", help="R2 に上げない")
    args = ap.parse_args()
    ep = args.ep
    if not EP_ID.match(ep):
        sys.exit(f"回の ID の形が違う: {ep}（例: 2026-11-22 / 2026-11-22-2）")
    ep_dir = os.path.join(ROOT, "episodes", ep)

    lock = open(os.path.join(ROOT, ".daily.lock"), "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        sys.exit("別の実行が動いている")

    git("pull", "--ff-only")
    if glob.glob(os.path.join(ep_dir, "script_*.txt")):
        log("台本は作成済み。生成をとばす")
    else:
        os.makedirs(ep_dir, exist_ok=True)
        generate(ep, episode_number(ep))
    for _ in range(EXPAND_TRIES):
        chars = validate(ep_dir)
        if chars >= TARGET_CHARS:
            break
        expand(ep, chars)
    validate(ep_dir)

    wait_engine()
    log("音声合成")
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "synthesize.py"), ep_dir], check=True)

    verb = "Update" if git("ls-files", f"episodes/{ep}").stdout.strip() else "Add"
    git("add", f"episodes/{ep}", "config/readings.json")
    if git("diff", "--cached", "--quiet", check=False).returncode:
        with open(os.path.join(ep_dir, "notes.md"), encoding="utf-8") as f:
            title = f.readline().removeprefix("# ").strip()
        git("commit", "-m", f"{verb} episode {title}")
        log("コミットした")
    if not args.no_push:
        git("push")
        log("push した")
    if not args.no_publish:
        subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "publish.py")], check=True)
        log("R2 に公開した")
    log(f"完了: {os.path.join(ep_dir, 'episode.mp3')}")


if __name__ == "__main__":
    main()
