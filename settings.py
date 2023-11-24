# VoivoClip
#
# アプリケーション設定クラス
#
# Copyright (c) 2023 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import json
import threading

from voicevox_api import VoicevoxAPI

class Settings:
    def __init__(self, setting_file_path):
        self._setting_file_path = setting_file_path
        self._lock = threading.Lock()
        self._init_member()

    def _init_member(self):
        self._speaker_id = 3
        self._speed_scale = 1.0
        self._pitch_scale = 0.0
        self._voicevox_server = VoicevoxAPI.DEFALUT_SERVER

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

    # 設定ファイルを保存する
    def save(self):
        with self._lock:
            self._save_nolock()

    def _save_nolock(self):
        with open(self._setting_file_path, "w", encoding="utf-8") as file:
            setting = {}
            setting["speaker_id"] = self._speaker_id
            setting["speed_scale"] = self._speed_scale
            setting["pitch_scale"] = self._pitch_scale
            setting["voicevox_server"] = self._voicevox_server
            json.dump(setting, file, ensure_ascii=False, indent=4)

    # 設定ファイルを読み込む
    def load(self):
        with self._lock:
            try:
                with open(self._setting_file_path, "r", encoding="utf-8") as file:
                    setting = json.load(file)
                    self._speaker_id = setting["speaker_id"]
                    self._speed_scale = setting["speed_scale"]
                    self._pitch_scale = setting["pitch_scale"]
                    self._voicevox_server = setting["voicevox_server"]
                return setting
            except Exception as err:
                self._init_member()
                self._save_nolock()
