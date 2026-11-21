# ふかぼりテックラジオ

その日いちばん話題になった技術トピックを1つ選び、ニュースではなく「技術そのもの」を2人の掛け合いで約40分深掘りするポッドキャストを、毎朝自動で作る。追加費用0円が前提。

台本の書き方は `docs/format.md` を参照。

## 構成（予定）
1. 05:00 Claude Code のルーティン: トピック選定 → 調査 → 台本（`episodes/<日付>/script_*.txt`）と概要欄（`notes.md`）を作ってコミット
2. WSL の GPU で AivisSpeech Engine による音声合成 → mp3
3. Cloudflare R2（`podcast.hiradekeishi.com`）に mp3 と RSS を公開
4. スマホのポッドキャストアプリで RSS を購読し、自動ダウンロードしてオフラインで聴く

## 台本の書式
1行1発言。`T|` は解説役（タカミ）、`Y|` は聞き手（ユウ）。

## ローカルで音声を作る
```bash
# AivisSpeech Engine を localhost:10101 で起動しておく
python3 scripts/synthesize.py episodes/2026-11-21
```
英単語の読み方は `config/readings.json` に足していく。

## WSL での毎朝の自動実行
音声合成は GitHub Actions ではなく、WSL の GPU（RTX 5060）で行う。40分の回が約3分でできる。

- エンジン: `~/opt/aivisspeech/`（Linux 版 1.2.0）。CUDA 12 / cuDNN 9 は同じフォルダの venv に pip で入れ、`start.sh` が `LD_LIBRARY_PATH` に通す（sudo 不要）。
- 声モデル（`.aivmx`）は `~/.local/share/AivisSpeech-Engine/Models/` に置く。リポジトリは公開なのでコミットしない。
- systemd ユーザーユニット（`~/.config/systemd/user/`）:
  - `aivisspeech.service`: エンジンを常に起動しておく
  - `fukabori-daily.timer`: 毎朝 05:00 に `fukabori-daily.service` を動かす。PC が止まっていて逃した場合は、次に起動したときに動く
- `scripts/daily.py`: `prompts/daily.md` を使って `claude -p` に台本を書かせる → 書式と字数を確かめる → 音声を作る → コミットして push。止まっても、再実行すれば続きから進む。ログは `logs/<日付>.log`。

## 公開（Cloudflare R2）
Pages は使わず、R2 バケット `fukabori-radio` に置いて `podcast.hiradekeishi.com` で公開している（無料枠: 保存10GB、転送量は無料）。

- 購読用の URL: **https://podcast.hiradekeishi.com/feed.xml**
- バケットの中身: `feed.xml` / `cover.jpg` / `episodes/<日付>.mp3`
- `scripts/publish.py`: `episodes/*/notes.md` と mp3 から RSS を作り、まだ上げていない mp3 とカバー、RSS を wrangler で上げる。`daily.py` の最後で呼ばれる
- 番組名・説明は `config/podcast.json`
- wrangler は `npx wrangler@4 login` でログインした状態を使う（トークンは自動で更新される）

```bash
python3 scripts/publish.py --dry-run                    # work/feed.xml を作るだけ
python3 scripts/daily.py --date 2026-11-22 --no-push --no-publish   # 手で1回分を作る
systemctl --user list-timers fukabori-daily.timer      # 次に動く時刻
journalctl --user -u aivisspeech -f                    # エンジンのログ
```

## 声とクレジット
- 解説: 阿井田 茂（Calm）CV：古山キリヲ / ACML 1.0
- 聞き手: M2（Style-Bert-VITS2 付属の男性モデル）/ CC BY-SA 4.0
- 音声合成: AivisSpeech
