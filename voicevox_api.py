# VoivoClip
#
# VOICEVOX APIクラス
#
# Copyright (c) 2023 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import json
import requests

from voicevox_speaker import VoicevoxSpeaker

class VoicevoxAPI:
    DEFALUT_SERVER = "http://127.0.0.1:50021"
    server = DEFALUT_SERVER

    # 話者リストを取得する
    @classmethod
    def get_speakers(cls):
        try:
            response = requests.get(f"{VoicevoxAPI.server}/speakers")
            response.raise_for_status()
            items = response.json()
            speakers = []
            for item in items:
                styles = item["styles"]
                for style in styles:
                    speakers.append(VoicevoxSpeaker(style["id"], item["name"], style["name"]))
            return speakers
        except Exception as err:
            print(err)
            return None
        
    # テキストの読み上げ用データを取得する
    @classmethod
    def audio_query(clas, text, speaker_id):
        post_params = {"text": text, "speaker": speaker_id}
        response = requests.post(f"{VoicevoxAPI.server}/audio_query", params=post_params)
        response.raise_for_status()
        return response.json()

    # 音声データを生成する
    @classmethod
    def synthesis(clas, query_json, speaker_id):
        post_params = {"speaker": speaker_id}
        response = requests.post(f"{VoicevoxAPI.server}/synthesis", params=post_params, data=json.dumps(query_json))
        response.raise_for_status()
        return response.content
