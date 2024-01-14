# VoivoClip
#
# アプリケーション設定クラス
#
# Copyright (c) 2023-2024 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import json
import os
import threading

from voicevox import Voicevox
from voicevox_api import VoicevoxAPI

class Settings:
    FILE_VER = 2

    def __init__(self, setting_file_path):
        self._setting_file_path = setting_file_path
        self._lock = threading.Lock()
        self._init_member()

    def _init_member(self):
        self._speaker_id = 3
        self._speed_scale = 1.2
        self._pitch_scale = 0.0
        self._voicevox_server = VoicevoxAPI.DEFALUT_SERVER
        self._voicevox_install_path = Voicevox.DEFAULT_INSTALL_PATH

    # 話者ID
    def get_speaker_id(self):
        with self._lock:
            return self._speaker_id

    def set_speaker_id(self, speaker_id):
        with self._lock:
            self._speaker_id = speaker_id

    # 読み上げスピード
    def get_speed_scale(self):
        with self._lock:
            return self._speed_scale

    def set_speed_scale(self, speed_scale):
        with self._lock:
            self._speed_scale = speed_scale

    # 声の高さ
    def get_pitch_scale(self):
        with self._lock:
            return self._pitch_scale

    def set_pitch_scale(self, pitch_scale):
        with self._lock:
            self._pitch_scale = pitch_scale

    # VOICEVOX サーバーのURL
    def get_voicevox_server(self):
        with self._lock:
            return self._voicevox_server
    
    def set_voicevox_server(self, voicevox_server):
        with self._lock:
            self._voicevox_server = voicevox_server

    # VOICEVOX のインストールパス
    def get_voicevox_install_path(self):
        with self._lock:
            return self._voicevox_install_path
    
    def set_voicevox_install_path(self, install_path):
        with self._lock:
            self._voicevox_install_path = install_path

    # 設定ファイルを保存する
    def save(self):
        with self._lock:
            self._save_nolock()

    def _save_nolock(self):
        with open(self._setting_file_path, "w", encoding="utf-8") as file:
            setting = {}
            setting["file_ver"] = Settings.FILE_VER
            setting["speaker_id"] = self._speaker_id
            setting["speed_scale"] = self._speed_scale
            setting["pitch_scale"] = self._pitch_scale
            setting["voicevox_server"] = self._voicevox_server
            setting["voicevox_install_path"] = self._voicevox_install_path
            json.dump(setting, file, ensure_ascii=False, indent=4)

    # 設定ファイルを読み込む
    def load(self):
        if not os.path.exists(self._setting_file_path):
            self._init_member()
            self._save_nolock()
            return

        with self._lock:
            with open(self._setting_file_path, "r", encoding="utf-8") as file:
                setting = json.load(file)
                file_ver = setting.get("file_ver", 1)
                self._speaker_id = setting.get("speaker_id", self._speaker_id)
                self._speed_scale = setting.get("speed_scale", self._speed_scale)
                self._pitch_scale = setting.get("pitch_scale", self._pitch_scale)
                self._voicevox_server = setting.get("voicevox_server", self._voicevox_server)
                self._voicevox_install_path = setting.get("voicevox_install_path", self._voicevox_install_path)

        if file_ver < Settings.FILE_VER:
            self._save_nolock()
