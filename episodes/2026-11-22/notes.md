# #002 ただの文字を送っただけで、なぜサーバーは乗っ取られるのか（2026-11-22）

大文字のエーを64個とイコールを1個——ただの文字列が、なぜジャバで書かれたサーバーの乗っ取りにつながるのか。今週立て続けに公開された3つの脆弱性（OpenJDK の Base64 デコーダ「Java4Shell」、OpenSSL の Base64 エンコード、Ruby の大文字変換「ruby2ßhell」）を入り口に、その奥にある共通構造を40分で掘り下げます。Base64 が電子メールのために生まれた理由（7ビットの通り道、uuencode、PEM、MIME）、なぜ64なのか・末尾のイコールの正体、バッファオーバーフローの歴史（モリスワーム、メモリ安全性が脆弱性の約7割を占める現実）、整数あふれ・ドイツ語のエスツェット（ß→SS）という「長さは変わらない」という思い込み、SIMD（AVX-512）による高速化と、安全なはずのジャバが手書きアセンブリ（イントリンシック）へ処理を外出しするとき安全性の保証が切れること、そして端数のそのまた端数で符号を読み違えて書き込み範囲のマスクが全開になる仕組みまで。最後に、攻守の両側がAIでバグを探し始めた現在地と、「見つけるのは安くなったが、検証は人間の責任として残る」という前回（カリー・ハワード対応の回）との接続で締めます。骨は一本——データを別の形に変えるとき、新しい長さの見積もりが一か所ずれると、箱からはみ出す。

※ この台本はAI（Claude）の支援で作成しています。
※ 題材のひとつ ruby2ßhell の公式クレジットには、発見者として Anthropic（Claude の開発元）が含まれます。番組の制作にも Claude を用いているため、その点にご留意ください。
※ 3件はいずれも公開から数日の事案で、発見者の主張・検証中の内容を多く含みます。深刻度評価（特に OpenSSL の件）や悪用可能性については、台本中でもそのつど「主張の段階」と断っています。
※ イメージをつかむため、厳密さを捨てて単純化して説明しています。攻撃の具体的な手順には立ち入っていません。

## 出典・参考
- Java4Shell（CVE-2026-114938）発見者 Calif の解説: https://calif.io/java4shell
- Java4Shell 解説（JFrog Security Research）: https://research.jfrog.com/post/java4shell-vulnerability/
- Java4Shell 解説（Semgrep）: https://semgrep.dev/blog/2026/java4shell-openjdk-base64-vulnerability/
- OpenJDK の AVX-512 Base64 デコード高速化（JDK-8268276, Intel / Scott Gibbons, 2021）: https://bugs.openjdk.org/browse/JDK-8268276
- ruby2ßhell（Ruby2Shell）発見者 Veria Labs の解説: https://verialabs.com/ruby2shell/
- Ruby 公式セキュリティ告知（2026-11-18）: https://www.ruby-lang.org/en/news/2026/11/18/multiple-vulnerabilities-in-regexp-and-string/
- OpenSSL EVP_EncodeBlock() の件（CVE-2026-121481, GitHub Advisory）: https://github.com/advisories/GHSA-83xj-7xh4-4p7x
- OpenSSL 修正 PR: https://github.com/openssl/openssl/pull/33652
- Base64 の仕様（RFC 4648, Simon Josefsson, 2006）: https://www.rfc-editor.org/rfc/rfc4648
- MIME の Base64 は1行76文字以内（RFC 2045, 1996）: https://www.rfc-editor.org/rfc/rfc2045
- PEM の Base64 は1行64文字（RFC 1421, 1993）: https://www.rfc-editor.org/rfc/rfc1421
- Base64 の歴史（Wikipedia）: https://en.wikipedia.org/wiki/Base64
- uuencode / Mary Ann Horton, 1980（Wikipedia）: https://en.wikipedia.org/wiki/Uuencoding
- SIMD による高速化: Muła & Lemire「Faster Base64 Encoding and Decoding Using AVX2 Instructions」(ACM TWEB, 2018): https://arxiv.org/abs/1704.00605
- Muła & Lemire「Base64 encoding and decoding at almost the speed of a memory copy」(SPE, 2020): https://arxiv.org/abs/1910.05109
- Aleph One「Smashing the Stack for Fun and Profit」(Phrack 49, 1996): http://phrack.org/issues/49/14.html
- ファジングの起源（Barton Miller, 1988 嵐の夜の着想）と Miller, Fredriksen & So「An Empirical Study of the Reliability of UNIX Utilities」(CACM, 1990): https://pages.cs.wisc.edu/~bart/fuzz/
- Heartbleed（CVE-2014-0160）: https://heartbleed.com/
- メモリ安全性が脆弱性の約7割という調査（Microsoft, BlueHat IL 2019, Matt Miller）: https://github.com/microsoft/MSRC-Security-Research/blob/master/presentations/2019_02_BlueHatIL/2019_01%20-%20BlueHatIL%20-%20Trends%2C%20challenge%2C%20and%20shifts%20in%20software%20vulnerability%20mitigation.pdf

## クレジット
- 音声合成: AivisSpeech
- 解説（タカミ）: 阿井田 茂（CV：古山キリヲ）
- 聞き手（ユウ）: M2（Style-Bert-VITS2 付属モデル / CC BY-SA 4.0）
