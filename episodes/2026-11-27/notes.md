# #008 値がひとつもない型に、なぜ十年もかかったのか（2026-11-27）

プログラミング言語 Rust で、十年と五回の失敗を経て、ようやく「何もない型」——never 型（`!`）——が普通の型として使えるようになりました（Rust 1.100, 2026-11-12）。値をひとつも持たない型は何の役に立つのか、そして、なぜそんなものを入れるのに十年もかかったのか。型を「値の袋」として数える見方（bool は2、ユニット型や void は実は1、never は0）から始め、戻ってこない式の型としての never、どんな型にもなれる理由（空集合と「偽からは何でも言える」）、TypeScript の網羅性チェックの「おまじない」の正体、Result<T, !> と型の算数（足せば消え、掛ければゼロ）、メモリ配置への効き目、標準ライブラリの仮の型 Infallible までを掘り下げます。後半は、2015年の RFC 1216 から、2018年・2019年の安定化と取り消し、そして本当の壁だった「型推論のフォールバック」——誰も書いていないのに事実上仕様になっていた既定値 `()`——の話へ。既定値を動かすとコンパイルが通らなくなるコード、さらに unsafe の中で黙って未定義動作に変わるコード（objc の例）、エディションとクレーターを使った七段階の移行計画、約3,300クレートへの影響と、バックポートで回った地道な作業。最後に、never は停止の証明ではないこと、パニックとの関係など、落とし穴と限界を整理します。

※ この台本はAI（Claude）の支援で作成しています。
※ リリース自体は2026-11-12。InfoQ の記事（2026-11-25）をきっかけに改めて話題になったため、この日の題材にしました。
※ 「五回の失敗」の内訳は公式告知に列挙されておらず、台本では記録の確認できた2018年・2019年の2回のみ具体的に扱っています（2018年の件は報道ベース）。影響を受けたクレートの数などは LWN の記事・言語チームの議事録に基づくもので、数え方には幅があります。
※ イメージをつかむため、厳密さを捨てて単純化して説明しています。

## 出典・参考
- Announcing Rust 1.100.0（Rust 公式ブログ, 2026-11-12）: https://blog.rust-lang.org/2026/11/12/Rust-1.100.0/
- Rust Project Goal 2026「Stabilize the never type」: https://goals.rust-lang.org/2026/stabilize-never-type.html
- RFC 1216「Promote `!` to a type」(2015): https://rust-lang.github.io/rfcs/1216-bang-type.html
- 追跡 issue #35121「Tracking issue for promoting `!` to a type」: https://github.com/rust-lang/rust/issues/35121
- 1.41 での安定化 PR #65355 / 取り消し PR #67224: https://github.com/rust-lang/rust/pull/65355 / https://github.com/rust-lang/rust/pull/67224
- 最終的な安定化 PR #155499: https://github.com/rust-lang/rust/pull/155499
- Rust Edition Guide「Never type fallback change」: https://doc.rust-lang.org/edition-guide/rust-2024/never-type-fallback.html
- T-lang 設計会議の議事録「2024-04-05: Never type」: https://hackmd.io/@rust-lang-team/BkK6HupyR
- lint `never_type_fallback_flowing_into_unsafe`（PR #123939）: https://doc.rust-lang.org/stable/nightly-rustc/rustc_lint/builtin/static.NEVER_TYPE_FALLBACK_FLOWING_INTO_UNSAFE.html
- LWN「Stabilizing Rust's never type」(Daroc Alden, 2026-09-08): https://lwn.net/Articles/1091015/
- InfoQ「Rust 1.100 Ships the Never Type After Ten Years and Five Failed Attempts」(2026-11-25): https://www.infoq.com/news/2026/11/rust-1-100-never-types/
- ComputingForGeeks「Rust Never Type Stable: What Breaks and the Fix」: https://computingforgeeks.com/rust-never-type/
- FOSSLinux「Rust 1.100 Ships the Never Type After a Decade」: https://www.fosslinux.com/163936/rust-1-100-never-type-stabilized.htm
- TypeScript 2.0 リリースノート（never 型）: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-2-0.html

## クレジット
- 音声合成: AivisSpeech
- 解説（タカミ）: 阿井田 茂（CV：古山キリヲ）
- 聞き手（ユウ）: M2（Style-Bert-VITS2 付属モデル / CC BY-SA 4.0）
