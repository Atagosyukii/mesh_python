## リポジトリの説明
MESHをpythonで動かすプログラムファイルを集めたリポジトリです。

- sample〇〇.py となっているものは以下のMESHの公式ドキュメントからコピーしてきたものです（一部修正）。
  - https://developer.meshprj.com/hc/ja/articles/9164308204313-Python
- shootingGallerySystem.py は独自のプログラムです。以下に詳細を示します。


## shootingGallerySystem について
これは射的のHIT判定をMESHを使って検知しようという目的で開発されました。
MESHアプリを使わない理由は、HIT判定に利用するにはレイテンシーが大きかったためです。

MESHの動きブロックを的に付け、的が倒れたことを動きブロックが検知し、通知を出します。
この通知を利用して、何らかのフィードバックを低いレイテンシーで返すことができます。
(フィードバックの部分はまだ開発中です。)


## 必要なもの

- MESH ブロック

  - ソフトウェアバージョン : 1.2.5
 
- Bluetooth 4.0 以上を搭載した端末

  - 対応OSは、Windows 10、Mac OS、Linux です。（Python のライブラリ bleak に依存）

- ソフトウェア

  - Python
    - バージョン 3.9 以上が必要です。
  - bleak


## 準備
1. Python の実行環境がない場合、事前にセットアップを行ってください。
2. お使いの端末のターミナル上で以下のコマンドを実行し、bleak ライブラリをインストールします。
```
pip install bleak
```
3. MESH ブロックの電源を入れ、プログラムを動作させる PC 等のそばに置きます。


## トラブルシューティング
プログラムを実行した際、MESHブロックとの初回接続でWinエラーなどと表示されプログラムが停止する場合、MESHブロックのバージョンが古い可能性があります。
MESHアプリからブロックをアップデートしてください。


## ライセンス
MESH ブロック 技術文書のライセンスを継承しています。

Original document by Sony Marketing Inc., is licensed under CC BY 4.0.
https://developer.meshprj.com
https://creativecommons.org/licenses/by/4.0/
