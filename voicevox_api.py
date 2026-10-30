# VoivoClip
#
# VOICEVOX APIクラス
#
# Copyright (c) 2023-2026 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import requests

from voicevox_speaker import VoicevoxSpeaker


class VoicevoxAPIError(Exception):
    """VOICEVOX APIの呼び出しまたは応答処理に失敗した。"""


class VoicevoxAPI:
    DEFALUT_SERVER = "http://127.0.0.1:50021"
    CONNECT_TIMEOUT = 3
    HEALTH_CHECK_TIMEOUT = (CONNECT_TIMEOUT, 3)
    REQUEST_TIMEOUT = (CONNECT_TIMEOUT, 30)
    SYNTHESIS_TIMEOUT = (CONNECT_TIMEOUT, 120)
    server = DEFALUT_SERVER

    # バージョンを取得する
    @staticmethod
    def get_version():
        try:
            response = requests.get(
                f"{VoicevoxAPI.server}/version",
                timeout=VoicevoxAPI.HEALTH_CHECK_TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, ValueError) as err:
            raise VoicevoxAPIError(
                "Failed to get the VOICEVOX version"
            ) from err

    # 話者リストを取得する
    @staticmethod
    def get_speakers():
        try:
            response = requests.get(
                f"{VoicevoxAPI.server}/speakers",
                timeout=VoicevoxAPI.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            items = response.json()

            if not isinstance(items, list):
                raise ValueError("Speakers response is not an array")

            speakers = []
            for item in items:
                styles = item["styles"]
                for style in styles:
                    speakers.append(VoicevoxSpeaker(style["id"], item["name"], style["name"]))
            return speakers
        except (
            requests.exceptions.RequestException,
            ValueError,
            KeyError,
            TypeError,
        ) as err:
            raise VoicevoxAPIError(
                "Failed to get speakers from VOICEVOX"
            ) from err
        
    # テキストの読み上げ用データを取得する
    @staticmethod
    def audio_query(text, speaker_id):
        try:
            post_params = {"text": text, "speaker": speaker_id}
            response = requests.post(
                f"{VoicevoxAPI.server}/audio_query",
                params=post_params,
                timeout=VoicevoxAPI.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            query = response.json()

            if not isinstance(query, dict):
                raise ValueError("Audio query response is not an object")

            return query
        except (requests.exceptions.RequestException, ValueError) as err:
            raise VoicevoxAPIError(
                "Failed to create an audio query"
            ) from err

    # 音声データを生成する
    @staticmethod
    def synthesis(query_json, speaker_id):
        try:
            post_params = {"speaker": speaker_id}
            response = requests.post(
                f"{VoicevoxAPI.server}/synthesis",
                params=post_params,
                json=query_json,
                timeout=VoicevoxAPI.SYNTHESIS_TIMEOUT,
            )
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as err:
            raise VoicevoxAPIError(
                "Failed to synthesize speech"
            ) from err
