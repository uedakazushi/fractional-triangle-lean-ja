# 公開手順

現在はローカルの公開候補です。GitHub リポジトリの作成・push は行っていません。

1. `python3 scripts/configure_publication.py --owner OWNER` で公開先を設定します。
2. 英語正本を先に確定・公開し、その HTTPS URL と正確な commit SHA を
   `upstream.lock.json` に設定します。移動する `main` には固定しません。
3. 固定版の正本を指定して、日本語 Blueprint の宣言・HTML/PDF・リンクを検査します。
4. ファイル一覧を確認して GitHub に push します。CI は固定版の英語正本を checkout し、
   ビルド・宣言検査・サイト生成を行います。
5. Pages を GitHub Actions から配信する設定にして、Pages ワークフローを手動実行します。
   実際のアップロード前には、GitHub 上で CI が通過したとは主張しません。

コード Apache-2.0、解説 CC BY 4.0 は著者指定済みです。
引用時は正本の固定 commit SHA を併記してください。
