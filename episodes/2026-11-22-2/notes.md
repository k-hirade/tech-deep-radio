# #003 オブザーバビリティの正体は、ダッシュボードではなかった（2026-11-22）

「オブザーバビリティ」は監視をおしゃれに言い換えた流行語なのか——。その出どころをたどると、1960年にルドルフ・カルマンが制御理論で立てた「外から見える出力だけで、中の状態を言い当てられるか」という問いに行き着きます。可観測性はツールではなくシステムの性質であること、監視（事前のアサーション）とオブザーバビリティ（事後の質問）の違い、ツイッターのオブザーバビリティチームと、Parse〜Facebook の Scuba〜Honeycomb へと続くチャリティー・メジャーズの物語、ログ・メトリクス・トレースの三本柱、カーディナリティの爆発、平均が隠す遅さと「The Tail at Scale」の63%の計算、Google の Dapper から Zipkin・Jaeger、W3C Trace Context による文脈の受け渡し、OpenTracing と OpenCensus の合流で生まれた OpenTelemetry と「名前の合意」（セマンティック・コンベンション）、eBPF 計装の強みと限界、ワイドイベントと「オブザーバビリティ2.0」（主張の段階）、費用・オーバーヘッド・個人情報・欠けたテレメトリーという落とし穴、そしてAIエージェントの観測までを掘り下げます。今回は番組の持ち主からのテーマ指定回です。

※ この台本はAI（Claude）の支援で作成しています。
※ 「オブザーバビリティ2.0」やAIエージェントの観測の有効性は、提唱者・各社の主張や試行の段階を含むため、台本中でもそのつど「主張の段階」と断っています。
※ イメージをつかむため、厳密さを捨てて単純化して説明しています。

## 出典・参考
- R. E. Kalman「On the General Theory of Control Systems」(1960) と可観測性（Wikipedia）: https://en.wikipedia.org/wiki/Observability
- Twitter Engineering「Observability at Twitter」(2013): https://blog.x.com/engineering/en_us/a/2013/observability-at-twitter
- Scuba: Diving into Data at Facebook (VLDB 2013): https://research.facebook.com/publications/scuba-diving-into-data-at-facebook/
- Charity Majors ほか『Observability Engineering』(O'Reilly, 2022): https://www.oreilly.com/library/view/observability-engineering/9781492076438/
- Peter Bourgon「Metrics, tracing, and logging」(2017): https://peter.bourgon.org/blog/2017/02/21/metrics-tracing-and-logging.html
- Etsy「Measure Anything, Measure Everything」(StatsD, 2011): https://www.etsy.com/codeascraft/measure-anything-measure-everything
- Prometheus: https://prometheus.io/docs/introduction/overview/
- Dean & Barroso「The Tail at Scale」(CACM, 2013): https://research.google/pubs/the-tail-at-scale/
- Google SRE 本「Monitoring Distributed Systems」（4つのゴールデンシグナル）: https://sre.google/sre-book/monitoring-distributed-systems/
- Sigelman ほか「Dapper, a Large-Scale Distributed Systems Tracing Infrastructure」(Google, 2010): https://research.google/pubs/dapper-a-large-scale-distributed-systems-tracing-infrastructure/
- Zipkin: https://zipkin.io/
- Jaeger: https://www.jaegertracing.io/
- W3C Trace Context: https://www.w3.org/TR/trace-context/
- OpenTelemetry: https://opentelemetry.io/
- OpenTelemetry Blog「When Missing Telemetry Is the Signal」: https://opentelemetry.io/blog/2026/when-missing-telemetry-is-the-signal/
- OpenTelemetry Blog「Deprecating the Collector Batch Processor」: https://opentelemetry.io/blog/2026/collector-batching-migration/
- OpenTelemetry at KubeCon NA 2026: https://opentelemetry.io/blog/2026/kubecon-na/
- CNCF「Observability Day」at KubeCon NA 2026: https://www.cncf.io/blog/2026/09/24/observability-day-where-the-community-comes-together-at-kubecon-cloudnativecon-north-america-2026/
- Charity Majors「Is it time to version observability? (Signs point to yes)」: https://www.honeycomb.io/blog/time-to-version-observability-signs-point-to-yes
- Charity Majors インタビュー（TechTarget）: https://www.techtarget.com/it-infrastructure/podcast/Charity-Majors-on-AI-observability-and-the-future-of-SRE

## クレジット
- 音声合成: AivisSpeech
- 解説（タカミ）: 阿井田 茂（CV：古山キリヲ）
- 聞き手（ユウ）: M2（Style-Bert-VITS2 付属モデル / CC BY-SA 4.0）
