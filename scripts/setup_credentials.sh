#!/usr/bin/env bash
# 権限を絞ったトークンを ~/.config/fukabori/ に保存する。入力は画面に表示されない。
#   - R2: fukabori-radio バケットだけ Object Read & Write の API トークン（Access Key ID / Secret Access Key）
#   - GitHub: tech-deep-radio だけ Contents: Read and write の fine-grained トークン
# このリポジトリの git push だけがそのトークンを使うように設定する。
set -euo pipefail
DIR="$HOME/.config/fukabori"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$DIR" && chmod 700 "$DIR"
umask 077

ENV="$DIR/r2.env"
ACCOUNT_ID="$(grep -s '^R2_ACCOUNT_ID=' "$ENV" | cut -d= -f2 || true)"
if [ -z "$ACCOUNT_ID" ]; then read -rp "Cloudflare Account ID: " ACCOUNT_ID; fi
read -rp  "R2 Access Key ID: " AK
read -rsp "R2 Secret Access Key（表示されません）: " SK; echo
printf 'R2_ACCOUNT_ID=%s\nR2_ACCESS_KEY_ID=%s\nR2_SECRET_ACCESS_KEY=%s\n' "$ACCOUNT_ID" "$AK" "$SK" > "$ENV"

read -rsp "GitHub fine-grained token（表示されません）: " GH; echo
printf '%s\n' "$GH" > "$DIR/github-token"

# このリポジトリだけ、保存したトークンで push する（全体の設定には触らない）
git -C "$REPO" config --local --replace-all credential.https://github.com.helper ""
git -C "$REPO" config --local --add credential.https://github.com.helper \
  '!f() { echo username=x-access-token; echo "password=$(cat "$HOME/.config/fukabori/github-token")"; }; f'

echo "保存しました: $ENV, $DIR/github-token"
