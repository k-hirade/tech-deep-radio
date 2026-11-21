#!/usr/bin/env python3
"""Turn an episode script (script_*.txt, lines "T|..." / "Y|...") into one mp3 with AivisSpeech Engine."""
import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
import urllib.parse
import urllib.request

ENGINE = os.environ.get("AIVIS_ENGINE", "http://localhost:10101")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 話者ごとの声と話し方（AivisSpeech Engine のスタイルID）
VOICES = {
    "T": {"style_id": 1310138977, "speed": 1.0, "pitch": 0.0},  # 解説: 阿井田 茂 (Calm)
    "Y": {"style_id": 1368642336, "speed": 1.02, "pitch": 0.0},  # 聞き手: M2 (ノーマル)
}
PAUSE_SAME = 0.25   # 同じ話者が続くときの間（秒）
PAUSE_SWITCH = 0.45  # 話者が交代するときの間（秒）


def load_readings():
    path = os.path.join(ROOT, "config", "readings.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def apply_readings(text, readings):
    for word in sorted(readings, key=len, reverse=True):
        text = re.sub(rf"(?<![A-Za-z]){re.escape(word)}(?![A-Za-z])", readings[word], text)
    return text


def synth(text, voice, out_path):
    params = urllib.parse.urlencode({"text": text, "speaker": voice["style_id"]})
    req = urllib.request.Request(f"{ENGINE}/audio_query?{params}", method="POST")
    query = json.load(urllib.request.urlopen(req))
    query["speedScale"] = voice["speed"]
    query["pitchScale"] = voice["pitch"]
    query["prePhonemeLength"] = 0.05
    query["postPhonemeLength"] = 0.05
    req = urllib.request.Request(
        f"{ENGINE}/synthesis?speaker={voice['style_id']}",
        data=json.dumps(query).encode(),
        headers={"Content-Type": "application/json"},
    )
    with open(out_path, "wb") as f:
        f.write(urllib.request.urlopen(req).read())


def silence(path, seconds):
    if not os.path.exists(path):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                        "anullsrc=r=44100:cl=mono", "-t", str(seconds), path], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode_dir")
    ap.add_argument("--bitrate", default="48k")
    args = ap.parse_args()

    readings = load_readings()
    lines = []
    for path in sorted(glob.glob(os.path.join(args.episode_dir, "script_*.txt"))):
        with open(path, encoding="utf-8") as f:
            for raw in f:
                raw = raw.strip()
                if raw:
                    speaker, text = raw.split("|", 1)
                    lines.append((speaker, text))

    work = os.path.join(args.episode_dir, "work")
    os.makedirs(work, exist_ok=True)
    pause_same = os.path.join(work, f"pause_{PAUSE_SAME}.wav")
    pause_switch = os.path.join(work, f"pause_{PAUSE_SWITCH}.wav")
    silence(pause_same, PAUSE_SAME)
    silence(pause_switch, PAUSE_SWITCH)

    parts = []
    prev = None
    for i, (speaker, text) in enumerate(lines):
        voice = VOICES[speaker]
        spoken = apply_readings(text, readings)
        key = hashlib.sha1(json.dumps([voice, spoken], ensure_ascii=False).encode()).hexdigest()[:12]
        wav = os.path.join(work, f"{key}.wav")
        if not os.path.exists(wav):
            synth(spoken, voice, wav)
        if prev is not None:
            parts.append(pause_same if prev == speaker else pause_switch)
        parts.append(wav)
        prev = speaker
        if (i + 1) % 50 == 0:
            print(f"{i + 1}/{len(lines)}", flush=True)

    list_path = os.path.join(work, "concat.txt")
    with open(list_path, "w") as f:
        for p in parts:
            f.write(f"file '{os.path.abspath(p)}'\n")
    out = os.path.join(args.episode_dir, "episode.mp3")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ac", "1", "-ar", "44100",
                    "-b:a", args.bitrate, out], check=True)
    print(out)


if __name__ == "__main__":
    main()
