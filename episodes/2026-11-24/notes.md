# #005 パープレキシティの正体は、ファイルの縮み具合だった（2026-11-24）

AIの賢さを測る数字「パープレキシティ」の正体は、ファイルを圧縮したときの縮み具合と同じものだった——。OpenAI のチーフサイエンティスト、ヤクブ・パホツキが自社モデルのパープレキシティの推移を公開し、それを知能の共通の物差しにしようと提案した件を入り口に、「予測＝圧縮」という技術そのものを掘り下げます。どんなファイルも縮む魔法の圧縮はない（鳩の巣原理）、モールス信号と「よく出るものを短く」、1948年にクロード・シャノンが定義した「驚き」としての情報量とエントロピー、情報源符号化定理。1951年の当てっこゲームで英語のエントロピーが1文字あたり約0.6〜1.3ビットと見積もられたこと、送る側と受け取る側が「同じ予言者」を持てば外れた分だけ送ればよいという圧縮の芯。期末試験の代わりのレポートから生まれたハフマン符号と、整数ビットの切り上げという限界、1976年の算術符号と特許の時代（bzip2 がハフマンに戻した理由）。1977年に IBM のジェリネクらが音声認識のために提案したパープレキシティ（何択で迷っているか）、学習の損失が圧縮後のビット数そのものであること、対数の底とトークナイザーの違いという読み方の落とし穴とビット毎バイト。後半は、予言を突き詰めると知識や推論が要るという階段、ソロモノフとコルモゴロフの「一番短いプログラム」、展開プログラムの大きさまで数えるハッター賞、言語モデルで画像や音声を専用形式より小さくした実験と、モデル自身の大きさを足すと逆に約140倍にふくらむというねじれ、GPU の計算の非決定性と算術符号、未知の「床」。最後に、社内コードという評価データ・汚染・gzip 分類論文の採点バグ・「間違いまで上手に真似る」問題・思考の連鎖が数字に映らない問題を疑い、物差しの提案がルール作りの提案でもあることまでを扱います。

※ この台本はAI（Claude）の支援で作成しています。
※ 題材の OpenAI の文章は、「共有の」基準の提案部分で Anthropic（Claude の開発元）CEO ダリオ・アモデイの文章にリンクしており、台本でもその点に触れています。番組の制作に Claude を用いているため、ご留意ください。
※ パープレキシティの数値は OpenAI 社内の評価データ（社内コードの固定スナップショット）での自社測定で、対数の底は明記されていません。「この値を切ると新しい能力が出る」という読み方や、パープレキシティを知能の共通基準にする提案は主張の段階で、台本中でもそう断っています。
※ シャノンが妻ベティに探偵小説の文字を当てさせた逸話は伝記に基づくもので、1951年の論文の被験者を特定するものではありません。エントロピーの命名やジェリネクの発言など、後から語られた逸話はそのように扱っています。
※ イメージをつかむため、厳密さを捨てて単純化して説明しています。

## 出典・参考
- Jakub Pachocki「Perplexity and Intelligence」(OpenAI, 2026-11-22): https://openai.com/index/perplexity-and-intelligence/
- Hacker News の議論: https://news.ycombinator.com/item?id=50601525
- Dario Amodei「We Must Pace the Frontier」(2026-09): https://darioamodei.com/post/we-must-pace-the-frontier
- frank chu「2.18 bits/byte: perplexity is just compression」(2026-11-22): https://dev.to/frankchu/218-bitsbyte-perplexity-is-just-compression-4bj3
- C. E. Shannon「A Mathematical Theory of Communication」(1948) と情報源符号化定理（Wikipedia）: https://en.wikipedia.org/wiki/Shannon%27s_source_coding_theorem
- C. E. Shannon「Prediction and Entropy of Printed English」(BSTJ, 1951): https://www.nokia.com/bell-labs/publications-and-media/publications/prediction-and-entropy-of-printed-english/
- シャノンとベティの当てっこの逸話（Jimmy Soni & Rob Goodman, Aeon）: https://aeon.co/essays/how-a-polymath-transformed-our-understanding-of-information
- ハフマン符号の発見（MAA Convergence）: https://old.maa.org/press/periodicals/convergence/discovery-of-huffman-codes
- 算術符号（Wikipedia）: https://en.wikipedia.org/wiki/Arithmetic_coding
- bzip2（Wikipedia）: https://en.wikipedia.org/wiki/Bzip2
- Jelinek, Mercer, Bahl & Baker「Perplexity—a measure of the difficulty of speech recognition tasks」(JASA, 1977): https://doi.org/10.1121/1.2016299
- Frederick Jelinek（Wikipedia）: https://en.wikipedia.org/wiki/Frederick_Jelinek
- Hutter Prize: https://www.hutter1.net/prize/index.htm
- Matt Mahoney「Rationale for a Large Text Compression Benchmark」: https://www.mattmahoney.net/dc/rationale.html
- Large Text Compression Benchmark: https://www.mattmahoney.net/dc/text.html
- Delétang et al.「Language Modeling Is Compression」(2023): https://arxiv.org/abs/2309.10668
- Hoffmann et al.「Training Compute-Optimal Large Language Models」(Chinchilla, 2022): https://arxiv.org/abs/2203.15556
- Ilya Sutskever「An Observation on Generalization」(Simons Institute, 2023-08-14): https://simons.berkeley.edu/talks/ilya-sutskever-openai-2023-08-14
- Fabrice Bellard「ts_zip」: https://bellard.org/ts_zip/
- Fabrice Bellard「NNCP」: https://bellard.org/nncp/
- Jiang et al.「Less is More: Parameter-Free Text Classification with Gzip」(ACL Findings, 2023) の採点方法への指摘（Ken Schutte, 2023-07）: https://kenschutte.com/gzip-knn-paper/

## クレジット
- 音声合成: AivisSpeech
- 解説（タカミ）: 阿井田 茂（CV：古山キリヲ）
- 聞き手（ユウ）: M2（Style-Bert-VITS2 付属モデル / CC BY-SA 4.0）
