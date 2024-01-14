# VoivoClip
#
# アプリケーションクラス
#
# Copyright (c) 2023-2024 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import sys
from tkinter import messagebox

from settings import Settings
from voicevox import Voicevox
from voicevox_api import VoicevoxAPI

APP_NAME = "VoivoClip"
APP_VERSION = "0.2.1"
COPYRIGHT = "Copyright 2023-2024 led-mirage"

SETTING_FILE = "settings.json"

class Application:
    # コンストラクタ
    def __init__(self):
        self.speakers = None
        self.settings = None
        pass

    # 開始
    def start(self):
        self.print_apptitle()

        self.settings = Settings(SETTING_FILE)
        self.settings.load()

        VoicevoxAPI.server = self.settings.get_voicevox_server()
        Voicevox.run_voicevox(self.settings.get_voicevox_install_path())

        self.speakers = VoicevoxAPI.get_speakers()
        if self.speakers is None:
            message = "VOICEVOX を起動してから使ってね"
            print(message)
            messagebox.showerror(f"{APP_NAME}", message)
            sys.exit()

        from main_window import MainWindow
        main_window = MainWindow(self)
        main_window.show()
        main_window.terminate()
    
    # タイトルを表示する
    def print_apptitle(self):
        print(f"----------------------------------------------------------------------")
        print(f" {APP_NAME} {APP_VERSION}")
        print(f"")
        print(f" {COPYRIGHT}")
        print(f"----------------------------------------------------------------------")
        print(f"")

if __name__ == "__main__":
    from application import Application
    app = Application()
    app.start()
