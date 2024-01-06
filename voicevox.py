# VoivoClip
#
# VOICEVOX 制御用クラス
#
# Copyright (c) 2023-2024 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import os
import subprocess
import time

from voicevox_api import VoicevoxAPI

class Voicevox:
    DEFAULT_INSTALL_PATH = "%LOCALAPPDATA%/Programs/VOICEVOX/VOICEVOX.exe"

    @staticmethod
    def run_voicevox(voicevox_path=DEFAULT_INSTALL_PATH):
        if not Voicevox.is_voicevox_running():
            appdata_local = os.getenv("LOCALAPPDATA")
            voicevox_path = voicevox_path.replace("%LOCALAPPDATA%", appdata_local)
            if os.path.isfile(voicevox_path):
                subprocess.Popen(voicevox_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(1)
                while not Voicevox.is_voicevox_running():
                    time.sleep(1)
                return True
            else:
                return False
        else:
            return True
    
    @staticmethod
    def is_voicevox_running():
        version = VoicevoxAPI.get_version()
        if version is not None:
            return True
        else:
            return False
