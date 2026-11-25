# #007 行列のかけ算の本当の速さは、なぜ半世紀も決まらなかったのか（2026-11-26）

二行二列の行列のかけ算は、掛け算八回ではなく七回でできる——1969年のシュトラッセンの発見から始まった「行列積の指数 ω」をめぐる半世紀を掘り下げます。OpenAI が11月24日に公開したプレプリント「The matrix multiplication exponent is nine fourths」（ω はちょうど 9/4 だとする主張）を入り口に、なぜ足し算は数えず掛け算だけを数えるのか（分割統治と指数）、コルモゴロフの予想を一週間で覆したカラツバの掛け算、アルゴリズム探しがテンソルのランク（立方体の表の分解）と同じであること、ウィノグラードによる「2×2は7回が最小」の証明と、3×3ですら未解決という現状、AlphaTensor と AlphaEvolve による探索。パンの 2.795、ビーニらの近似（ボーダーランク）、シェーンハーゲの「まとめ買い」不等式、シュトラッセンのレーザー法、コッパースミス＝ウィノグラードの 2.3755 から小数点以下七桁を争った2010年代、そしてレーザー法そのものの限界を示したアンバイニスらの障壁。後半は、10月の上限 9/4（多項式のかけ算とシュトラッセンの漸近スペクトルによる道）と、ザウダムら・シュピルカら人間の研究者による追試と解説、11月の下限の主張（速すぎる行列積があれば「重複チェック」の網をありえないほど圧縮できてしまう、という背理法）を扱います。最後に、ω は現実の速さではないこと（銀河的アルゴリズム、GPU が3乗のやり方を使う理由、数値安定性、算術回路というモデルの限定）、Lean による形式化の範囲、AI が書いた数学を人間が確かめる速さという限界までを話します。

※ この台本はAI（Claude）の支援で作成しています。
※ 題材の当事者は OpenAI（論文の著者表記は「OpenAI」のみで、原稿は名前の公表されていない社内モデルが生成したと説明されています）で、Anthropic / Claude は当事者ではありません。ただし番組の制作に Anthropic の Claude を用いており、競合する企業の成果を扱っている点にご留意ください。
※ 下限（ω ≥ 9/4）は2026年11月24日公開のプレプリントの主張で、査読前です。放送時点で人間の研究者が独立に検証したという報告は確認できず、台本中でも「主張の段階」と断っています。Lean による形式化は、リポジトリの説明によれば割り算を使わない回路の場合に限られます。
※ 上限（ω ≤ 9/4）は10月公開のプレプリントの結果で、複数の研究者による解説・再証明（いずれも査読前）が出ています。
※ 漸近スペクトルを使った上限の議論、テンソルネットワークを使った下限の議論は、イメージをつかむため大幅に単純化しています。シュトラッセンが「普通のやり方の最適性を示そうとしていた」という逸話は、本人の後年の発言として広く紹介されているものです。
※ イメージをつかむため、厳密さを捨てて単純化して説明しています。

## 出典・参考
- OpenAI「The matrix multiplication exponent is nine fourths」(2026-11-24): https://github.com/openai/math/tree/main/preprints/The-matrix-multiplication-exponent-is-nine-fourths-November-24-2026
- 同 PDF: https://raw.githubusercontent.com/openai/math/main/preprints/The-matrix-multiplication-exponent-is-nine-fourths-November-24-2026/paper.pdf
- OpenAI「An Upper Bound of 9/4 for the Matrix Multiplication Exponent」(2026-10): https://github.com/openai/math/tree/main/preprints/Matrix-Multiplication-Nine-Fourths-October-2-2026
- openai/math リポジトリの説明: https://github.com/openai/math
- Hacker News の議論: https://news.ycombinator.com/item?id=50637220
- Amanov, van den Berg, Zuiddam「Multiplying matrices via polynomials: exposition and barriers」(2026-10-21): https://arxiv.org/abs/2610.30054
- Amir Shpilka「Exposition of OpenAI's Matrix Multiplication in Exponent 9/4 (and an explicit algorithm)」ECCC TR26-281 (2026-10-27): https://eccc.weizmann.ac.il/report/2026/281/
- Baitian Li「Semidirect sums of tensors and the matrix multiplication exponent」(2026-11-03): https://arxiv.org/abs/2611.04175
- Doğan, Lysikov, Sakabe, Walter「Tensor value and the 9/4 bound for matrix multiplication」(2026-11-06): https://arxiv.org/abs/2611.09716
- Dupont ほか「Improving the matrix multiplication exponent with modern optimization and AlphaEvolve」(2026-08): https://arxiv.org/abs/2608.16884
- Scott Aaronson, Shtetl-Optimized（2026-11-25 の記事）: https://scottaaronson.blog/
- Emanuele Viola「Welcome to the golden age of computational complexity theory」(2026-11-24): https://emanueleviola.wordpress.com/
- 「OpenAI's claim that the matrix multiplication exponent is exactly 9/4, and what has been checked」(DEV Community): https://dev.to/axrisi/openais-claim-that-the-matrix-multiplication-exponent-is-exactly-94-and-what-has-been-checked-398j
- alphaXiv の論文ページ: https://www.alphaxiv.org/abs/2611.matrix-multiplication-exponent-lower-bound
- Volker Strassen「Gaussian elimination is not optimal」(1969): https://doi.org/10.1007/BF02165411
- A. A. Karatsuba「The Complexity of Computations」(1995): https://www.mathnet.ru/eng/tm1062
- Coppersmith, Winograd「Matrix multiplication via arithmetic progressions」(1990): https://doi.org/10.1016/S0747-7171(08)80013-2
- Ambainis, Filmus, Le Gall「Fast Matrix Multiplication: Limitations of the Coppersmith-Winograd Method」(2015): https://arxiv.org/abs/1411.5414
- Alman, Duan, Vassilevska Williams, Xu, Xu, Zhou「More Asymmetry Yields Faster Matrix Multiplication」(2024): https://arxiv.org/abs/2404.16349
- Cohn, Umans「A Group-theoretic Approach to Fast Matrix Multiplication」(2003): https://arxiv.org/abs/math/0307321
- Fawzi ほか「Discovering faster matrix multiplication algorithms with reinforcement learning」(Nature, 2022): https://www.nature.com/articles/s41586-022-05172-4
- Google DeepMind「AlphaEvolve」(2025): https://deepmind.google/discover/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/
- Matrix multiplication algorithm（Wikipedia）: https://en.wikipedia.org/wiki/Matrix_multiplication_algorithm
- Galactic algorithm（Wikipedia）: https://en.wikipedia.org/wiki/Galactic_algorithm

## クレジット
- 音声合成: AivisSpeech
- 解説（タカミ）: 阿井田 茂（CV：古山キリヲ）
- 聞き手（ユウ）: M2（Style-Bert-VITS2 付属モデル / CC BY-SA 4.0）
