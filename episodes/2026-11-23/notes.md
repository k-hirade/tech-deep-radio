# #004 コイン投げで作ったランキングは、なぜ今になって捨てられたのか（2026-11-23）

ゲームのランキング表の裏側は、十五年以上「コイン投げ」で作られていた——。Redis のソート済みセットを支えてきたスキップリストを、フォーク先の Valkey が B+ 木（fbtree）に置き換えた件を入り口に、その奥にある技術を掘り下げます。配列とリストの「探しやすさと直しやすさの綱引き」、平衡木の回転地獄、ウィリアム・ピューが1989〜1990年に示した「乱数生成器に相談して釣り合いを取る」発想、antirez が2010年に語ったスキップリスト採用の3つの理由、順位を対数時間で返すための「スパン」、同点は名前順という並べ方、listpack への切り替え。後半は、計算量が数える「比較の回数」と現実の速さを決める「メモリまで取りに行く回数」のずれ（キャッシュとメインメモリで約200倍）、1970年にボーイングの研究所で Bayer と McCreight が生んだ B 木と「B の意味」の逸話、B+ 木の葉の連結、そして Valkey の 61 分岐・512 バイトの葉・スコアと名前を詰めた値・4 バイトの「特徴量」と SIMD 比較までを追います。最後に「43%」が何の数字か、単一環境での測定、削除後に葉を合体しない割り切り、内部形式名の変更という互換性の問題、並行書き込みではいまもスキップリストが強いこと（Java の ConcurrentSkipListMap、LevelDB / RocksDB）、Dragonfly の先行例と antirez 自身の再実装の主張までを扱います。

※ この台本はAI（Claude）の支援で作成しています。
※ ベンチマークの数値は Valkey 開発者による単一環境・合流前ブランチでの測定です。antirez による Redis 側の実装の効果や、AI 支援で複雑さが扱えるようになったという見方は本人の主張の段階で、台本中でもそう断っています。fbtree の同点の並べ方・順位の計算方法は、プルリクエストの記述からの読み取りを含みます。
※ イメージをつかむため、厳密さを捨てて単純化して説明しています。

## 出典・参考
- Valkey Blog「From Skiplists to B+ Trees: Making Valkey Sorted Sets More Memory Efficient」(2026-11-16, Rain Valentine / Dragos Andriciuc): https://valkey.io/blog/from-skiplist-to-b+tree/
- Valkey PR #4206「ZSET B+ Tree PR 3: Replace skiplist with FB+ Tree implementation」: https://github.com/valkey-io/valkey/pull/4206
- Hacker News の議論: https://news.ycombinator.com/item?id=50534387
- William Pugh「Skip Lists: A Probabilistic Alternative to Balanced Trees」(CACM 33(6), 1990): https://homepage.cs.uiowa.edu/~ghosh/skip.pdf
- William Pugh「A Skip List Cookbook」: https://cgi.di.uoa.gr/~k08/manolis/2024-2025/lectures/skip_list_cookbook.pdf
- Skip list（Wikipedia）: https://en.wikipedia.org/wiki/Skip_list
- antirez によるスキップリスト採用理由（Hacker News, 2010-03-06）: https://news.ycombinator.com/item?id=1171934
- Redis の sorted set 実装（t_zset.c）: https://github.com/redis/redis/blob/7.2/src/t_zset.c
- Redis 設定ファイル（listpack の閾値）: https://github.com/redis/redis/blob/unstable/redis.conf
- Bayer & McCreight「Organization and Maintenance of Large Ordered Indexes」(Acta Informatica, 1972) と B 木（Wikipedia）: https://en.wikipedia.org/wiki/B-tree
- Douglas Comer「The Ubiquitous B-Tree」(ACM Computing Surveys, 1979): https://dl.acm.org/doi/10.1145/356770.356776
- Latency Numbers Every Programmer Should Know: https://gist.github.com/jboner/2841832
- Luo et al.「Bridging Cache-Friendliness and Concurrency: A Locality-Optimized In-Memory B-Skiplist」(2025): https://arxiv.org/abs/2507.21492
- Dragonfly「Dragonfly's New Sorted Set Implementation」(2024): https://www.dragonflydb.io/blog/dragonfly-new-sorted-set
- Java ConcurrentSkipListMap: https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/ConcurrentSkipListMap.html
- Keir Fraser「Practical lock-freedom」(2004): https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-579.pdf
- Valkey の沿革: https://valkey.io/topics/history/

## クレジット
- 音声合成: AivisSpeech
- 解説（タカミ）: 阿井田 茂（CV：古山キリヲ）
- 聞き手（ユウ）: M2（Style-Bert-VITS2 付属モデル / CC BY-SA 4.0）
