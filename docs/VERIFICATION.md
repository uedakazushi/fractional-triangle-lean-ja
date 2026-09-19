# 手で確認する手順

1. 英語正本を `upstream.lock.json` のコミットに合わせ、`bash scripts/verify.sh` を実行します。
   独立した全 clean 再ビルドには、専用の依存を持つ checkout で `bash scripts/acceptance.sh` を使います。
2. `formal/CanonicalRoots/Final.lean` の四定理と、
   `formal/CanonicalRoots/TheoremOneFour.lean` の `theorem_1_4` を読みます。
   `formal/` で `lake env lean FinalSignature.lean` を実行し、全引数を確認します。
3. `Target.lean` と `Semantics.lean` を開き、実複素商環、捩れを保持した次数群、
   根の等式、全複素点での孤立性、次数保存付き AlgEquiv を確認します。
   列挙への所属や未証明分類が対象の仮定に入っていないことが重要です。
4. `EquationRealizes` と `HasCanonicalParameter` を展開して、最小生成元数と
   実 Ext 加群の次数が意図した数学の意味になっているか読みます。
5. `lake env lean Audit.lean` の結果を監査します。許容公理は
   `propext`、`Classical.choice`、`Quot.sound` のみです。
   公理監査が通っても、定義や仮定が意図したものかは別に読む必要があります。
   定理1.4については `InvertiblePolynomial`、`IsPrincipal`、
   `HigherRootRigidity` を展開し、六つの連言を原稿4ページと照合します。
   三変数の逆方向には atomic 型への所属や根環としての実現を仮定していません。
6. `OutputCertificates.lean` の証明書は行ごとの検査でなく全リスト等式です。
   Python の一致試験や SHA256 は外部検査であり、Lean の証明ではありません。
7. Blueprint の本文と Lean 宣言を照合します。緑色や宣言の実在検査だけでは
   自然言語の説明が正しいことは保証されません。

本リポジトリの `scripts/check_blueprint.py --source PATH --lean` は正本の固定コミット、
両言語の宣言・辺の一致、宣言の Lean 内での実在と公理許容範囲を検査します。
正本の過去ログと今回の公開用検査は区別して記録されています。
