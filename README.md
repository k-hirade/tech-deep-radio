# ふかぼりテックラジオ

その日いちばん話題になった技術トピックを1つ選び、ニュースではなく「技術そのもの」を2人の掛け合いで約40分深掘りするポッドキャストを、毎朝自動で作る。追加費用0円が前提。

台本の書き方は `docs/format.md` を参照。

## 構成（予定）
1. 05:00 Claude Code のルーティン: トピック選定 → 調査 → 台本（`episodes/<日付>/script_*.txt`）と概要欄（`notes.md`）を作ってコミット
2. GitHub Actions: AivisSpeech Engine で音声合成 → mp3
3. Cloudflare Pages（`podcast.hiradekeishi.com` 予定）に mp3 と RSS を公開
4. スマホのポッドキャストアプリで RSS を購読し、自動ダウンロードしてオフラインで聴く

## 台本の書式
1行1発言。`T|` は解説役（タカミ）、`Y|` は聞き手（ユウ）。

## ローカルで音声を作る
```bash
# AivisSpeech Engine を localhost:10101 で起動しておく
python3 scripts/synthesize.py episodes/2026-11-21
```
英単語の読み方は `config/readings.json` に足していく。

## 声とクレジット
- 解説: 阿井田 茂（Calm）CV：古山キリヲ / ACML 1.0
- 聞き手: M2（Style-Bert-VITS2 付属の男性モデル）/ CC BY-SA 4.0
- 音声合成: AivisSpeech
