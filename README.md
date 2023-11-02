# shootingGallerySystem について
これは射的のHIT判定をMESHを使って検知しようという目的で開発されました。
MESHアプリを使わない理由は、HIT判定に利用するにはレイテンシーが大きいと考えられていたためです。
(実際は動きブロックの通知においてはほとんどありませんでした。)

MESHの動きブロックを的に付け、的が倒れたことを動きブロックが検知し、通知を出します。
この通知を利用して、何らかのフィードバックを低いレイテンシーで返すことができます。

このプログラムではGPIOブロックの電源出力をオンオフしています。
これをリレーにつなぎ、LEDテープなどの装飾・ロボットの動作の制御などに使用できます。

## 必要なもの

- MESH ブロック

  - ソフトウェアバージョン : 1.2.5
 
- Bluetooth 4.0 以上を搭載した端末

  - 対応OSは、Windows 10、Mac OS、Linux です。（Python のライブラリ bleak に依存）

- ソフトウェア

  - Python
    - バージョン 3.9 以上が必要です。
  - bleak
  - pygame
    - サウンドの再生に使用します。

## 準備
1. Python の実行環境がない場合、事前にセットアップを行ってください。
2. お使いの端末のターミナル上で以下の2つのコマンドを実行し、bleak と pygame をインストールします。
```
pip install bleak
pip install pygame
```
3. MESH ブロックの電源を入れ、プログラムを動作させる PC 等のそばに置きます。

### 使用するブロック
- 動きブロック (的が倒れた際の判定に使用します)
- LEDブロック (インジケーターライトとして使用します)
- GPIOブロック * 2 (的が倒れた際のフィードバックに使用します)
- ボタンブロック (GPIOブロックのフィードバックを停止する際に使用します)

ブロックが不足していてもプログラムは動作します。
 
### config.ini ファイルの用意
MESHブロックを一意に特定するための config.ini ファイルを用意する必要があります。

プログラムと同じディレクトリに作成し、中身は以下のように記述してください。それぞれの「=」の後にMESHブロックの Complete Local Name を入力します (ACブロックのようにしてください) 。

Complete Local Name が記述されていない場合、そのブロックは無いものとしてプログラムが動きます。

```
[MESH_DEVICES]
MESH-100AC = MESH-100AC{7桁のシリアルナンバー}
MESH-100LE = 
MESH-100GP1 = 
MESH-100GP2 = 
MESH-100BU = 
```

### サウンドの再生
現在74行目で指定した通りにファイルを設置しないと再生できませんが、後ほど改良します。

### プログラム実行から接続まで
1. 用意したブロックの電源を入れた状態でPCの付近に置き、プログラムを実行します。

2. ブロックのスキャンが始まり、config.ini ファイルに記載したブロックがすべて見つかると初回接続が行われます。

3. 全てのブロックとの接続が完了するとLEDブロックが緑色に3回点滅します。

これで接続作業が完了し、システムが動作するようになります。

### 動作の説明
ブロックの上面が変化した際に、動きブロックから通知が送信され、何らかのフィードバックが行われるようになっています。

- ブロックの上面が [表] か [裏] になった場合
  - LEDブロックが黄色に点灯し、GPIOブロックの電源出力がオンになる

- ブロックの上面が [左] か [右] か [上] か [下] になった場合
  - LEDブロックが黄色に点滅し、GPIOブロックの電源出力がオフになる

また、ボタンブロックからフィードバックを停止したり、システムを一時停止したりすることができます。

- ボタンブロックのボタンが2回押された場合
  - LEDブロックが青色に点灯する
  - GPIOブロックの電源出力がオフになる
- ボタンブロックのボタンが長押しされた場合
  - GPIOブロックの電源出力がオフになる
  - システムを一時停止するフラグが設定される
  - LEDブロックが赤色に点滅する
- ボタンブロックのボタンが1回押された場合
  - システムを一時停止するフラグが解除される
  - LEDブロックが緑色に3回点滅する

## トラブルシューティング
プログラムを実行した際、MESHブロックとの初回接続でWinエラーなどと表示されプログラムが停止する場合、MESHブロックのバージョンが古い可能性があります。
MESHアプリからブロックをアップデートしてください。

## ライセンス
MESH ブロック 技術文書のライセンスを継承しています。

Original document by Sony Marketing Inc., is licensed under CC BY 4.0.
https://developer.meshprj.com
https://creativecommons.org/licenses/by/4.0/
