# #006 ブラウザ作りの難しさの正体は、壊れたページを「みんなと同じように」間違えることだった（2026-11-25）

閉じタグの順番を間違えたエイチティーエムエルを、ブラウザはどう表示するのか——答えは「仕様に直し方が一字一句書いてある」でした。ゼロから書かれたブラウザ Ladybird が初のアルファ版を出した件を入り口に、「新しいブラウザエンジンを作るのは、なぜ不可能と言われるのか」を掘り下げます。主要エンジンが Blink・WebKit・Gecko の三つに収れんした経緯（KHTML から WebKit、Blink への枝分かれ、Opera の Presto と Edge の自前エンジンの終了）、ページが仕様ではなく多数派のブラウザに合わせて書かれるという構造。XHTML の厳しさが普及しなかった理由と、2004年の WHATWG 発足、イアン・ヒクソンが壊れた HTML の読み方を手順として書き下ろした HTML5 のパース仕様（84 状態のトークナイザー、21 の挿入モード、「養子縁組」アダプション・エージェンシー・アルゴリズム）。トッド・ファーナーの発案とタンテク・チェリクの実装に始まる互換モードと「ドクタイプの一行の本当の役目」、互換性とは過去のバグの保存であること。ホーコン・ウィウム・リーの CSS 提案とカスケード、幅は上から高さは下からというレイアウトの向き、IE の箱モデルと box-sizing、アシッドテスト。描画の流れ（パース・スタイル・レイアウト・ペイント・合成）、JIT の速さと危うさ、プロセス分離——ブラウザはほとんど OS であること。後半は、アンドレアス・クリングが依存症からの回復の途中で始めた SerenityOS から Ladybird への歩み、仕様の手順番号をそのままコメントに写す書き方、約200万の確認項目を持つ Web Platform Tests、AI エージェントによる機能の穴埋めと Rust への移植。最後に、テストの通過数と実用性の差、公開プルリクエストの受付停止、外部ライブラリへの依存、資金という限界までを扱います。

※ この台本はAI（Claude）の支援で作成しています。
※ Ladybird は、JavaScript エンジンの一部を Rust に移植する作業に Claude Code（Anthropic、Claude の開発元）と Codex を用いたと公表しており、台本でもその点に触れています。番組の制作に Claude を用いているため、ご留意ください。
※ Web Platform Tests の通過数は Ladybird 自身の発表に基づく数字で、確認項目の数え方には分野ごとの偏りがあります。AI で埋めた機能の長期的な品質、ベータ版・正式版の時期（2027年・2028年とする報道あり）は未確定で、台本中でも「主張の段階」と断っています。
※ イアン・ヒクソンが各ブラウザの振る舞いを調べて仕様を書いた経緯は、本人のインタビューと関係者の記録に基づいて単純化しています。Chromium の行数は測定時期により異なるため概数です。
※ イメージをつかむため、厳密さを捨てて単純化して説明しています。

## 出典・参考
- Andreas Kling「Ladybird is now in alpha」(2026-11-23): https://ladybird.org/posts/alpha/
- Hacker News の議論: https://news.ycombinator.com/item?id=50614249
- Ladybird ニュースレター（2026年10月）: https://ladybird.org/newsletter/2026-10-31/
- Ladybird ニュースレター（2026年7月）: https://ladybird.org/newsletter/2026-07-31/
- 「Ladybird adopts Rust, with help from AI」(2026-02-23): https://ladybird.org/posts/adopting-rust/
- 「Changing How We Develop Ladybird」(2026-06-05): https://ladybird.org/posts/changing-how-we-develop-ladybird/
- Ladybird Browser Initiative の発表（2024-07-01）: https://ladybird.org/posts/announcement
- Ladybird のコーディング規則（LibWebPatterns.md）: https://github.com/LadybirdBrowser/ladybird/blob/master/Documentation/LibWebPatterns.md
- Andreas Kling「Ladybird: A new cross-platform browser project」(2022): https://awesomekling.github.io/Ladybird-a-new-cross-platform-browser-project/
- SerenityOS（Wikipedia）: https://en.wikipedia.org/wiki/SerenityOS
- Simon Willison「Ladybird's first alpha release」: https://simonwillison.net/2026/Nov/23/ladybird/
- Drew DeVault「The reckless, infinite scope of web browsers」(2020): https://drewdevault.com/blog/Reckless-limitless-scope/
- StatCounter ブラウザのシェア: https://gs.statcounter.com/browser-market-share
- Don Melton の KDE 開発者へのメール（2003-01-07）: https://mail.kde.org/pipermail/kfm-devel/2003-January/002446.html
- Chromium Blog「Blink: A rendering engine for the Chromium project」(2013): https://blog.chromium.org/2013/04/blink-rendering-engine-for-chromium.html
- Servo、Linux Foundation Europe へ（Igalia, 2023）: https://www.igalia.com/2023/09/07/The-Servo-project-is-joining-Linux-Foundation-Europe.html
- WHATWG HTML 仕様「Parsing HTML documents」: https://html.spec.whatwg.org/multipage/parsing.html
- WHATWG FAQ: https://whatwg.org/faq
- W3C「XHTML 2 Working Group Expected to Stop Work End of 2009」: https://www.w3.org/news/2009/xhtml-2-working-group-expected-to-stop-work-end-of-2009-w3c-to-increase-resources-on-html-5
- Anne van Kesteren「HTML5 parser history」(2010): https://annevankesteren.nl/2010/05/html5-parser-history
- Ian Hickson による Google のページ分析の紹介（2006-01）: https://lists.whatwg.org/pipermail/whatwg-whatwg.org/2006-January/005616.html
- Ian Hickson インタビュー（HTML5 Doctor）: https://html5doctor.com/interview-with-ian-hickson-html-editor/
- Mozilla「The old HTML parser is dead」(2013): https://blog.mozilla.org/mrbkap/2013/08/12/the-old-html-parser-is-dead-long-live-the-html-parser/
- Quirks Mode Standard（WHATWG）: https://quirks.spec.whatwg.org/
- Tantek Çelik「Doctype switching」: https://tantek.com/notes/doctypeswitching.html
- Henri Sivonen「Activating Browser Modes with Doctype」: https://hsivonen.fi/doctype/
- MDN「Quirks Mode and Standards Mode」: https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Quirks_mode_and_standards_mode
- Håkon Wium Lie「Cascading HTML style sheets — a proposal」(1994): https://www.w3.org/People/howcome/p/cascade.html
- Acid2（Wikipedia）: https://en.wikipedia.org/wiki/Acid2
- Web Standards Project「Acid3 passed in 23 days」: https://www.webstandards.org/2008/04/07/acid3-passed-in-23-days/
- Matt Brubeck「Let's build a browser engine! Part 5: Boxes」(2014): https://limpet.net/mbrubeck/2014/09/08/toy-layout-engine-5-boxes.html
- Mariko Kosaka「Inside look at modern web browser (part 3)」(Google, 2018): https://developer.chrome.com/blog/inside-browser-part3
- Microsoft Edge「Super Duper Secure Mode」(2021): https://microsoftedge.github.io/edgevr/posts/Super-Duper-Secure-Mode/
- Apple のロックダウンモード発表（2022）: https://www.apple.com/newsroom/2022/07/apple-expands-commitment-to-protect-users-from-mercenary-spyware/
- Servo Blog「Servo and the Web Platform Tests」(2023): https://servo.org/blog/2023/07/20/servo-web-platform-tests
- wpt.fyi: https://wpt.fyi
- Interop 2026: https://web.dev/blog/interop-2026

## クレジット
- 音声合成: AivisSpeech
- 解説（タカミ）: 阿井田 茂（CV：古山キリヲ）
- 聞き手（ユウ）: M2（Style-Bert-VITS2 付属モデル / CC BY-SA 4.0）
