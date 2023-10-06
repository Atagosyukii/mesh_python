このリポジトリ内のプログラムは以下のドキュメントを参考にしています。また、2つのサンプルコードもそのままコピーしてあります。

https://developer.meshprj.com/hc/ja/articles/9164308204313-Python

必要なものや準備を以下に示します。

## 必要なもの
Python から操作するための環境として、以下を使用します。

- MESH ブロック

  - 必要な MESH ブロックのソフトウェアバージョンは1.2.5です。詳細はブロックソフトウェアバージョンについてを参考にしてください。
 
- Bluetooth 4.0 以上を搭載した端末

  - 対応OSは、Windows 10、Mac OS、Linux です。（Python のライブラリ bleak に依存）

- ソフトウェア

  - Python
    - バージョン 3.9 以上が必要です。
  - bleak

## 準備
1. Python の実行環境がない場合、事前にセットアップを行ってください。
2. お使いの端末のターミナル上で以下のコマンドを実行し、bleak ライブラリをインストールします。

```pip install bleak```

3. MESH ブロックの電源を入れ、プログラムを動作させる PC 等のそばに置きます。

## トラブルシューティング
プログラムを実行した際、MESHブロックとの初回接続でWinエラーなどと表示されプログラムが停止する場合、MESHブロックのバージョンが古い可能性があります。
MESHアプリからブロックをアップデートしてください。
