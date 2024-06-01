# <img src="image/application.ico" width="48"> VoivoClip

Copyright (c) 2023-2024 led-mirage

## 概要

クリップボードに貼り付けられたテキストを VOICEVOX で読み上げるアプリです。

[VOICEVOX公式ページ](https://voicevox.hiroshiba.jp/)

## スクリーンショット

<img width="189" alt="screenshot" src="https://github.com/led-mirage/VoivoClip/assets/139528700/3e06d108-3f5f-4c41-bcee-ad7fe6171a0e">

https://github.com/led-mirage/VoivoClip/assets/139528700/24307f87-4b5b-4f0c-837a-66c164acba4e

## 機能

- クリップボード監視の開始と停止
- キャラクター選択
- 話速調整（0.5～2.0）
- リピート
- 設定値の自動保存

## 動作確認環境

- Windows 11 Pro 23H2
- Python 3.12.0
- VOICEVOX 0.14.10 - 0.18.0
- VOICEVOX ENGINE 0.14.6 - 0.16.1

## 実行方法

### 🛩️ 実行ファイル（EXE）を使う場合

#### 1. プロジェクト用のフォルダの作成

任意の場所にプロジェクト用のフォルダを作成してください。

#### 2. アプリのダウンロード

以下のリンクから VoivoClip.ZIP をダウンロードして、作成したフォルダに展開してください。

https://github.com/led-mirage/VoivoClip/releases/tag/v0.3.1

#### 3. 実行

VOICEVOXを起動してから VoivoClip.exe または VoivoClipNC.exe をダブルクリックすればアプリが起動します。  
VoivoClip.exe はコンソールも一緒に起動するバージョンで、VoivoClipNC.exe はコンソールが起動しないバージョンです。  
※VOICEVOXが起動していない状態でアプリを開始すると、自動的にVOICEVOXを起動しようと試みます。

### 🛩️ Pythonで実行する場合

#### 1. プロジェクト用のフォルダの作成

任意の場所にプロジェクト用のフォルダを作成してください。

#### 2. ターミナルの起動

ターミナルかコマンドプロンプトを起動して、作成したプロジェクトフォルダに移動します。

#### 3. ソースファイルのダウンロード

ZIPファイルをダウンロードして作成したフォルダに展開してください。  
または、Gitが使える方は以下のコマンドを実行してクローンしてもOKです。

```bash
git clone https://github.com/led-mirage/VoivoClip.git
```

#### 4. ライブラリのインストール

以下のコマンドを実行して必要なライブラリをインストールします。

```bash
pip install -r requirements.txt
```

#### 5. 実行

VOICEVOX を起動したのち、以下のコマンドを実行するとアプリが起動します。  
※VOICEVOXが起動していない状態でアプリを開始すると、自動的にVOICEVOXを起動しようと試みます。

```bash
python application.py
```

## 設定

### ⚙️ アプリケーション設定ファイル（オプション）

`settings.json`ファイルにはこのアプリの設定情報が記載されています。

#### ✨ speaker_id（既定値 3）

VOICEVOXのキャラクターIDを記載します。アプリのGUIで設定できます。

#### ✨ speed_scale（既定値 1.2）

読み上げの速さの設定です。アプリのGUIで設定できます。

#### ✨ pitch_scale（既定値 0.0）

声の高さの設定です。声の高さを変更したい場合は、この値を編集してください。微妙な値で大きく変わる可能性があるので、0.1とか0.2刻みで調整するといいと思います。

#### ✨ voicevox_server（既定値 http://127.0.0.1:50021）

VOICEVOXのローカルサーバーのURLを記載します。普通は変更する必要はありません。

#### ✨ voicevox_install_path（既定値 %LOCALAPPDATA%/Programs/VOICEVOX/VOICEVOX.exe）

VOICEVOXを自動起動するために使用します。VOICEVOXの実行ファイルのパスを記載してください。VOICEVOXを既定の場所にインストールした場合は変更する必要はありません。別の場所にインストールした場合はこの値を変更してください。

#### ✨ replacements（既定値 []）

読み上げるテキストの置換設定です。置換対象（pattern）を正規表現で、置換後の文字列（replacement）を通常の文字列で指定します。

例えば括弧内のテキストと、URLを除去して読み上げたい場合は、以下のように設定します。置換パターンは複数個記載でき、上から順に処理されます。

```json
    "replacements": [
        {
            "pattern": "\\(.*?\\)|（.*?）",
            "replacement": ""
        },
        {
            "pattern": "https?:\\/\\/(?:[\\w\\-\\.]+)+(?:[\\w\\.\\/\\?%&=]*)?",
            "replacement": ""
        }
    ]
```

## 注意事項

### ⚡ ウィルス対策ソフトの誤認問題

このプログラムの実行ファイル（VoivoClip.exe、VoivoClipNC.exe）は PyInstaller というライブラリを使って作成していますが、ウィルス対策ソフトにマルウェアと誤認されることがあります。

もちろん、このアプリに悪意のあるプログラムは入っていませんが、気になる人は上記の「Pythonで実行する方法」で実行してください。

誤認問題が解決できるのが一番いいのですが、いい方法が見つかっていないので申し訳ありませんがご了承ください。

VirusTotalでのチェック結果は以下の通りです（2024/06/01 v0.3.1）

- VoivoClip.exe … 74個中4個のアンチウィルスエンジンで検出
- VoivoClipNC.exe … 74個中6個のアンチウィルスエンジンで検出

<img src="doc/virustotal_0.3.1.png" width="600">

## 使用しているライブラリ

### 🔖 requests 2.31.0

ホームページ： https://requests.readthedocs.io/en/latest/  
ライセンス：[Apache License 2.0](https://github.com/psf/requests/blob/main/LICENSE) 

### 🔖 pyperclip 1.8.2 

ホームページ： https://github.com/asweigart/pyperclip/tree/master  
ライセンス：[BSD 3-Clause "New" or "Revised" License](https://github.com/asweigart/pyperclip/blob/master/LICENSE.txt)

### 🔖 PyAudio 0.2.14

ホームページ： https://people.csail.mit.edu/hubert/pyaudio/  
ライセンス：[MIT License](https://people.csail.mit.edu/hubert/pyaudio/)

### 🔖 Pillow 10.2.0

ホームページ： https://python-pillow.org/  
ライセンス：[HPND License](https://raw.githubusercontent.com/python-pillow/Pillow/main/LICENSE)

## ライセンス

© 2023-2024 led-mirage

本アプリケーションは [MITライセンス](https://opensource.org/licenses/MIT) の下で公開されています。詳細については、プロジェクトに含まれる LICENSE ファイルを参照してください。

## バージョン履歴

### 0.1.0 (2023/11/24)

- ファーストリリース

### 0.2.0 (2024/01/06)

- 起動時に自動的にVOICEVOXの起動を試みるように変更
- 起動時のウィンドウの位置を右下に変更
- アプリケーションアイコンの追加
- その他、微修正

### 0.2.1 (2024/01/14)

- メソッド名修正（動作に影響なし）

### 0.2.2 (2024/02/04)

- ローカルPCでビルドしたをpyinstaller使用するよう変更（誤検知対策）
- pillowを10.2.0に更新
- VOICEVOX 0.16.1で動作確認

### 0.3.0 (2024/04/13)

- 置換文字列を設定できるように変更（正規表現で指定）

### 0.3.1 (2024/06/01)

- issue#3に対応（正規表現で置換する位置を変更）
