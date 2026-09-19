# Isolated hypersurface fractional triangle singularities — 日本語解説版

**著者：Kenji Hashimoto (橋本健治), Hwayoung Lee, Kazushi Ueda (植田一石)**

このリポジトリは、英語正本 `fractional-triangle-lean` の固定コミットに対応する
日本語解説です。Lean ソースを複製せず、正本の定理・定義へ接続する
[Lean Blueprint](blueprint/README.md) を収録します。

原稿の定理1.4も `CanonicalRoots.theorem_1_4` として英語正本に収録しています。
Blueprint の「原稿の定理1.4」節から、全次元の可逆表示、三変数の逆方向と
一意性、高次元の判定と剛性の証明を確認できます。

対象は `n ≥ 3`、`a ≥ 1` の孤立超曲面 canonical-root 環であり、同値関係は
次数付き複素代数同型です。`n` は最小生成元数、環の次元は `n−1`。
全ての孤立超曲面を分類するものではありません。

## 読み方

1. [数学的対象と四定理](docs/MATHEMATICS.md) で対象と保証を確認します。
2. Blueprint を開き、各定理の Lean ボタンから正本の実際の宣言を読みます。
3. [手動検証手順](docs/VERIFICATION.md) に沿って、定義・仮定・公理依存を確認します。

Lean ビルド・公理監査の通過と、人間の数学的査読は別です。
独立した人間による mathematical sign-off の完了は記録されていません。
この解説文の意味も Lean が自動認証するものではありません。

## Blueprint のビルド

Python 3.13、Graphviz、LuaLaTeX、latexmk、日本語 TeX が必要です。
英語正本を隣の `../fractional-triangle-lean` に置き、`upstream.lock.json` の
コミットへチェックアウトして、先にその `formal/` で `lake build` を実行します。

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r blueprint/requirements.txt
python scripts/check_blueprint.py --source ../fractional-triangle-lean --lean
python scripts/build_blueprint.py --source ../fractional-triangle-lean --pdf
python scripts/check_site.py
python -m http.server 8000 --directory _site
```

`http://localhost:8000/` から本文、依存グラフ、PDF、宣言ソースを開けます。
依存図は主要34項目の解説図で、全証明項の自動依存抽出ではありません。
正本と異なるコミットを与えると検査を失敗させます。

## 版と公開

[upstream.lock.json](upstream.lock.json) が対応する英語正本のコミットを固定します。
[PUBLICATION_VALIDATION.md](PUBLICATION_VALIDATION.md) に今回の検査結果を記録します。
[公開手順](docs/PUBLISHING.md) にリポジトリ間リンクと GitHub Pages の設定があります。
ローカルビルドだけでは GitHub へのアップロードは発生しません。

解説は [CC BY 4.0](LICENSES/CC-BY-4.0.txt)、補助コードは [Apache-2.0](LICENSE)。
引用時は [CITATION.cff](CITATION.cff) と正本の固定コミットを使用してください。

<!-- EDITION_LINKS -->
[English source](https://github.com/uedakazushi/fractional-triangle-lean) · [日本語解説](https://github.com/uedakazushi/fractional-triangle-lean-ja)
