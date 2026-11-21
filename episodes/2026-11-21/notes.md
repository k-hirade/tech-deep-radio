# #001 コンパイルが通ったら、数学の証明は終わるのか？（2026-11-21）

「プログラムを書くこと」と「数学の証明を書くこと」は、文字通り同じ作業だった——。命題は型、証明はプログラム（カリー・ハワード対応）から、数学的帰納法と再帰の関係、定理証明支援系 Lean の小さなカーネル、sorry や公理という抜け道、仕様の書き間違いという最後の落とし穴、AIが数学を最初に攻略した理由、seL4 や CompCert などのソフトウェア検証までを掘り下げます。題材は、Lean で1,700万行を超える一般化リーマン予想の証明が発表された件（収録時点では検証中の主張）。

※ この台本はAI（Claude）の支援で作成しています。題材の当事者にClaude（Anthropic）が含まれる点にご留意ください。
※ イメージをつかむため、厳密さを捨てて単純化して説明しています。

## 出典・参考
- Lean: https://lean-lang.org/
- Mathlib: https://github.com/leanprover-community/mathlib4
- Liquid Tensor Experiment（Peter Scholze の挑戦）: https://xenaproject.wordpress.com/2020/12/05/liquid-tensor-experiment/
- 四色定理の形式証明（Georges Gonthier, 2005/2008）: https://www.ams.org/notices/200811/tx081101382p.pdf
- Flyspeck（ケプラー予想の形式証明, 2014）: https://github.com/flyspeck/flyspeck
- seL4: https://sel4.systems/
- CompCert: https://compcert.org/
- Yang et al.「Finding and Understanding Bugs in C Compilers」(PLDI 2011): https://users.cs.utah.edu/~regehr/papers/pldi11-preprint.pdf
- AlphaProof（2024年の国際数学オリンピック）: https://deepmind.google/discover/blog/ai-solves-imo-problems-at-silver-medal-level/
- Levent Alpöge「remark」: https://alpo.ge/remark.pdf
- Terence Tao のブログ（2026-11-20）: https://terrytao.wordpress.com/2026/11/20/unforced-euler-singularity-unforced-navier-stokes-singularity-and-the-generalized-riemann-hypothesis/
- Scott Aaronson のブログ（2026-11-20）: https://scottaaronson.blog/?p=10344

## クレジット
- 音声合成: AivisSpeech
- 解説（タカミ）: 阿井田 茂（CV：古山キリヲ）
- 聞き手（ユウ）: M2（Style-Bert-VITS2 付属モデル / CC BY-SA 4.0）
