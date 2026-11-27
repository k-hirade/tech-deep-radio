# #009 三十年使われてきた素因数分解の速さに、いま証明がついたかもしれない（2026-11-28）

大きな数の素因数分解でいちばん速い方法「数体ふるい法」は、三十年以上どの記録でも使われてきました。ところがその速さは、「調べる数たちは、でたらめな数と同じくらい都合よく振る舞うはずだ」という仮定の上の見積もりで、証明はされていませんでした。今回は、試し割りとフェルマーの方法から始めて、「二乗と二乗の差」で数を割る発想、滑らかな数を集めてビットの XOR で二乗を作る仕組み、二次ふるい法と RSA-129 の解読、数体ふるい法までをたどります。

後半は、証明できる遅い方法と、証明できない速い方法のにらみ合いの歴史です。でたらめさを自分で持ち込んで証明につなげる作戦（Dixon、Lenstra–Pomerance、Lee–Venkatesan）を追い、11月25日に Google Research が公開した、AIエージェントが書いたという「仮定なしで L[1/3] の素因数分解」の論文が、どこを埋めたと主張しているのかを見ます。

ただし、この論文はまだ誰にも検証されていない主張の段階です。正しかったとしても、保証された時間は実際の数体ふるいよりはるかに遅く、RSA が破りやすくなる話ではありません。最後に、AKS 素数判定の前例と、TypeScript の型とテストの違いを手がかりに、「速くならない証明」に何の意味があるのかを考えます。

※ この台本はAI（Claude）の支援で作成しています。
※ 題材の論文は Google Research のリポジトリで公開されたもので、Cogentic（Gemini 4 を使う数学研究用のエージェント）が作成し、人の関与は最初の指示のみとされています。査読や第三者の検証は収録時点で確認できず、Lean による形式化も未公開です。台本中でもそのつど「主張の段階」と断っています。
※ 論文の本文（54ページ）は制作側で通読できておらず、内容の説明は要旨と各種の解説記事に基づいています。2048ビットでの計算量の比較（2^117、2^6400 など）や逆転する桁数は、公表された定数から番組側でざっくり見積もった値です。
※ RSA-129 の「4京年」は、当時リベストが示したと広く伝えられている見積もりです。
※ イメージをつかむため、厳密さを捨てて単純化して説明しています。

## 出典・参考
- Google Research「cogentic_research_papers」README（2026-11-25 の6本）: https://github.com/google-research/google-research/tree/master/cogentic_research_papers
- 論文「Unconditional Integer Factorization in Time L_N[1/3, O(1)]」: https://github.com/google-research/google-research/blob/master/cogentic_research_papers/integer_factorization/paper.pdf
- 論文「Unconditional Deterministic Subexponential Integer Factoring and Quadratic Nonresidue Construction」: https://github.com/google-research/google-research/tree/master/cogentic_research_papers/deterministic_factoring_l34
- 上記論文の要旨（alphaXiv）: https://www.alphaxiv.org/abs/2611.unconditional-integer-factorization
- Cogentic の論文（arXiv:2609.40324）: https://arxiv.org/abs/2609.40324
- Scott Aaronson のブログ（2026-11-25、コメント欄）: https://scottaaronson.blog/?p=10379
- 解説記事（Traictory）: https://traictory.com/news/2026-11-26-google-cogentic-factoring-papers
- 解説記事（getaibook）: https://getaibook.com/news/google-cogentic-six-papers-unconditional-factoring-lean/
- 解説記事（madrobot）: https://madrobot.blog/2026/11/26/google-cogentic-ai-factoring-proof-six-papers/
- Lee & Venkatesan「Rigorous analysis of a randomised number field sieve」(J. Number Theory, 2018): https://arxiv.org/abs/1805.08873
- Harvey & Hittmeir「A log-log speedup for exponent one-fifth deterministic integer factorisation」: https://arxiv.org/abs/2105.11105
- L記法（Wikipedia）: https://en.wikipedia.org/wiki/L-notation
- 数体ふるい法（Wikipedia）: https://en.wikipedia.org/wiki/General_number_field_sieve
- 二次ふるい法（Wikipedia）: https://en.wikipedia.org/wiki/Quadratic_sieve
- Dixon の方法（Wikipedia）: https://en.wikipedia.org/wiki/Dixon%27s_factorization_method
- RSA の挑戦問題と記録（Wikipedia）: https://en.wikipedia.org/wiki/RSA_numbers
- Agrawal, Kayal, Saxena「PRIMES is in P」(2002): https://www.cse.iitk.ac.in/users/manindra/algebra/primality_v6.pdf

## クレジット
- 音声合成: AivisSpeech
- 解説（タカミ）: 阿井田 茂（CV：古山キリヲ）
- 聞き手（ユウ）: M2（Style-Bert-VITS2 付属モデル / CC BY-SA 4.0）
