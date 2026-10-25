# スマホ用POスクリーナー

GitHub Pagesで `index.html` を公開し、GitHub Actionsが平日23:00 UTC（日本時間翌朝8:00）にStooqの日足ZIPを取得して `data.json` を更新します。

1. GitHubでPublicリポジトリを新規作成する。
2. このフォルダーの中身をリポジトリ直下へアップロードする。
3. Settings → Pages → Deploy from a branch → `main` / `/ (root)` を選ぶ。
4. Actionsから「POスクリーナー更新」を一度手動実行する。
5. 表示されたPagesのURLをスマホのホーム画面に追加する。

判定は終値ベースで、200日線の上昇と逆転待ちMA差1.5%以内を使います。無料GitHubの公開リポジトリで運用する想定です。
