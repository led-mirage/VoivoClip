# VoivoClip

Copyright (c) 2023 led-mirage

## 概要

クリップボードに貼り付けられたテキストを VOICEVOX で読み上げるアプリです。

## スクリーンショット

<img width="189" alt="screenshot" src="https://github.com/led-mirage/VoivoClip/assets/139528700/a820a011-5c20-474b-8c6e-281efe0d707d">

https://github.com/led-mirage/VoivoClip/assets/139528700/106c0770-c477-45c6-8d10-4a05c8e8a000

## 機能

- クリップボード監視の開始と停止
- キャラクター選択
- 話速調整（0.5～2.0）
- リピート
- 設定値の自動保存

## 動作確認環境

- Windows 11 Pro 23H2
- Python 3.12.0
- VOICEVOX 0.14.10
- VOICEVOX ENGINE 0.14.6

## 実行方法

### 実行ファイル（EXE）を使う場合

#### 1. プロジェクト用のフォルダの作成

任意の場所にプロジェクト用のフォルダを作成してください。

#### 2. アプリのダウンロード

以下のリンクから VoivoClip.ZIP をダウンロードして、作成したフォルダに展開してください。

https://github.com/led-mirage/VoivoClip/releases/tag/0.1.0

#### 3. 実行

VOICEVOX を起動したのち、VoivoClip.exeをダブルクリックすればアプリが起動します。

### Pythonで実行する場合

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

```bash
python application.py
```

## 使用しているライブラリ

### requests 2.31.0

ホームページ： https://requests.readthedocs.io/en/latest/  
ライセンス：[Apache License 2.0](https://github.com/psf/requests/blob/main/LICENSE) 

### pyperclip 1.8.2 

ホームページ： https://github.com/asweigart/pyperclip/tree/master  
ライセンス：[BSD 3-Clause "New" or "Revised" License](https://github.com/asweigart/pyperclip/blob/master/LICENSE.txt)

### PyAudio 0.2.14

ホームページ： https://people.csail.mit.edu/hubert/pyaudio/  
ライセンス：[MIT License](https://people.csail.mit.edu/hubert/pyaudio/)

### Pillow 10.1.0

ホームページ： https://python-pillow.org/  
ライセンス：[HPND License](https://raw.githubusercontent.com/python-pillow/Pillow/main/LICENSE)

## ライセンス

© 2023 led-mirage

本アプリケーションは [MITライセンス](https://opensource.org/licenses/MIT) の下で公開されています。詳細については、プロジェクトに含まれる LICENSE ファイルを参照してください。

## バージョン履歴

### 0.1.0 (2023/11/24)
- ファーストリリース




