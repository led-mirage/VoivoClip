# VoivoClip
#
# メインウィンドウクラス
#
# Copyright (c) 2023-2024 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import io
import os
import queue
import re
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import time
import threading
import wave

import pyperclip
import pyaudio
import requests
from PIL import Image, ImageTk

from application import Application, APP_NAME, APP_VERSION
from voicevox_api import VoicevoxAPI

App = None

class MainWindow:
    AUDIO_PARAMETER_SPECS = (
        {"name": "pitch_scale", "label": "高さ", "from": -0.15, "to": 0.15, "resolution": 0.01, "default": 0.0, "format": "{:.2f}"},
        {"name": "intonation_scale", "label": "抑揚", "from": 0.0, "to": 2.0, "resolution": 0.1, "default": 1.0, "format": "{:.1f}"},
        {"name": "volume_scale", "label": "音量", "from": 0.0, "to": 2.0, "resolution": 0.1, "default": 1.0, "format": "{:.1f}"},
        {"name": "pre_phoneme_length", "label": "前無音", "from": 0.0, "to": 1.5, "resolution": 0.01, "default": 0.1, "format": "{:.2f}"},
        {"name": "post_phoneme_length", "label": "後無音", "from": 0.0, "to": 1.5, "resolution": 0.01, "default": 0.1, "format": "{:.2f}"},
        {"name": "pause_length", "label": "間", "from": 0.0, "to": 1.5, "resolution": 0.01, "default": 0.1, "format": "{:.2f}"},
        {"name": "pause_length_scale", "label": "間倍率", "from": 0.01, "to": 2.0, "resolution": 0.1, "default": 1.0, "format": "{:.1f}"},
    )

    # コンストラクタ
    def __init__(self, app: Application):
        global App
        App = app

        self.monitoring = False
        self.stop_event = threading.Event()
        self.monitoring_thread = None
        self.speech_thread = None
        self.queue = queue.Queue()
        self.speech_queue = queue.Queue()
        self.last_speech_text = ""
        self.lock = threading.Lock()
        self.audio_param_controls = {}
        self.pause_length_auto = None

        self.root = tk.Tk()
        window_width = 410
        window_height = 380
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_right = int(screen_width - window_width - 20)
        position_down = int(screen_height - window_height - 100)
        self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

        self.root.resizable(False, False)
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        self.root.iconbitmap(self.resource_path("image/application.ico"))

        self.icon_start = self.load_icon(self.resource_path("image/start.png"))
        self.icon_start_gray = self.load_icon(self.resource_path("image/start_gray.png"))
        self.icon_stop = self.load_icon(self.resource_path("image/stop.png"))
        self.icon_stop_gray = self.load_icon(self.resource_path("image/stop_gray.png"))
        self.icon_repeat = self.load_icon(self.resource_path("image/repeat.png"))
        self.icon_repeat_gray = self.load_icon(self.resource_path("image/repeat_gray.png"))

        self.speaker_combo = self.create_speaker_combo()
        self.speed_label = self.create_speed_label()
        self.speed_scale = self.crate_speed_scale()
        self.start_button = self.create_start_button()
        self.stop_button = self.create_stop_button()
        self.repeat_button = self.create_repeat_button()
        self.audio_settings_frame = self.create_audio_settings_frame()

    # 終了処理
    def terminate(self):
        if self.monitoring:
            self.stop_event.set()
            self.monitoring_thread.join()
            self.speech_thread.join()

    # リソースのパスを取得する（PyInstallerでリソースを実行ファイルに入れるため）
    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    # ウィンドウを表示する
    def show(self):
        self.root.after(100, self.read_monitoring_thread_message, self.queue)
        self.layout()
        self.root.mainloop()

    # アイコンを読み込む
    def load_icon(self, path):
        image = Image.open(path)
        image = image.resize((16, 16), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)

    # 話者リストコンボボックスを作成する
    def create_speaker_combo(self):
        options = []
        current = 0
        for idx, speaker in enumerate(App.speakers):
            options.append(f"{speaker.name}（{speaker.style_name}）")
            if speaker.id == App.settings.get_speaker_id():
                current = idx
        combo = ttk.Combobox(self.root, values=options, width=34, state="readonly")
        combo.current(current)
        combo.bind("<<ComboboxSelected>>", self.speaker_changed)
        return combo

    # 話速ラベルを作成する
    def create_speed_label(self):
        label = tk.Label(self.root, text=f"話速：{App.settings.get_speed_scale():.1f}")
        return label

    # 話速スケールを作成する
    def crate_speed_scale(self):
        scale = tk.Scale(self.root, from_=0.5, to=2.0, resolution=0.1, length=160,
                         orient=tk.HORIZONTAL, showvalue=False, command=self.update_speed_label)
        scale.set(App.settings.get_speed_scale())
        scale.bind("<ButtonRelease-1>", self.speed_scale_changed)
        scale.bind("<FocusOut>", self.speed_scale_changed)
        return scale

    # 開始ボタンを作成する
    def create_start_button(self):
        button = tk.Button(self.root, text="開始", image=self.icon_start, width=60, height=36,
                           compound="left", padx=10, command=self.start_monitoring)
        return button

    # 停止ボタンを作成する
    def create_stop_button(self):
        button = tk.Button(self.root, text="停止", image=self.icon_stop, width=60, height=36,
                           compound="left", padx=10, command=self.stop_monitoring)
        return button

    # リピートボタンを作成する
    def create_repeat_button(self):
        button = tk.Button(self.root, image=self.icon_repeat, width=30, height=36, padx=10, command=self.repeat_speech)
        return button

    # 音声設定フレームを作成する
    def create_audio_settings_frame(self):
        frame = ttk.LabelFrame(self.root, text="音声設定")
        settings = App.settings.get_audio_query_setting_parameters()
        self.pause_length_auto = tk.BooleanVar(value=settings["pause_length"] is None)

        for row, spec in enumerate(MainWindow.AUDIO_PARAMETER_SPECS):
            name = spec["name"]
            value = settings[name]
            if value is None:
                value = spec["default"]

            label = tk.Label(frame, text=f"{spec['label']}：", width=7, anchor="w")
            scale = tk.Scale(frame, from_=spec["from"], to=spec["to"], resolution=spec["resolution"],
                             length=190, orient=tk.HORIZONTAL, showvalue=False)
            value_label = tk.Label(frame, text="", width=5, anchor="e")

            label.grid(row=row, column=0, padx=5, pady=2, sticky="w")
            scale.grid(row=row, column=1, padx=5, pady=2, sticky="w")
            value_label.grid(row=row, column=2, padx=5, pady=2, sticky="e")

            self.audio_param_controls[name] = {
                "scale": scale,
                "value_label": value_label,
                "format": spec["format"],
            }

            scale.set(value)
            scale.config(command=lambda scale_value, param_name=name: self.audio_param_changed(param_name, scale_value))
            scale.bind("<ButtonRelease-1>", self.audio_param_save)
            scale.bind("<FocusOut>", self.audio_param_save)

            if name == "pause_length":
                check = ttk.Checkbutton(frame, text="自動", variable=self.pause_length_auto,
                                        command=self.pause_length_auto_changed)
                check.grid(row=row, column=3, padx=5, pady=2, sticky="w")

            self.update_audio_param_label(name)

        self.update_pause_length_control_state()
        return frame

    # ウィジェットを配置する
    def layout(self):
        self.speaker_combo.grid(row=0, column=0, padx=5, pady=5, columnspan=8, sticky="w")
        self.speed_label.grid(row=1, column=0, padx=5, pady=5, columnspan=2, sticky="w")
        self.speed_scale.grid(row=1, column=2, padx=5, pady=5, columnspan=6, sticky="w")
        self.start_button.grid(row=2, column=0, padx=5, pady=5, columnspan=3, sticky="w")
        self.stop_button.grid(row=2, column=3, padx=5, pady=5, columnspan=3, sticky="w")
        self.repeat_button.grid(row=2, column=6, padx=5, pady=5, columnspan=2, sticky="w")
        self.audio_settings_frame.grid(row=3, column=0, padx=5, pady=5, columnspan=8, sticky="w")
        self.change_button_state()

    # 話者ドロップダウンリストの変更イベントハンドラ
    def speaker_changed(self, evnet):
        current = self.speaker_combo.current()
        App.settings.set_speaker_id(App.speakers[current].id)
        App.settings.save()

    # 話速ラベルの表示を更新する
    def update_speed_label(self, value):
        speed_scale = float(value)
        self.speed_label.config(text=f"話速：{speed_scale:.1f}")
        App.settings.set_speed_scale(speed_scale)

    # 話速スケールの変更イベントハンドラ
    def speed_scale_changed(self, event):
        App.settings.save()

    # 音声設定の変更イベントハンドラ
    def audio_param_changed(self, name, value):
        value = float(value)
        if name == "pause_length" and self.pause_length_auto.get():
            self.update_audio_param_label(name)
            return

        App.settings.set_audio_query_setting_parameter(name, value)
        self.update_audio_param_label(name)

    def audio_param_save(self, event=None):
        App.settings.save()

    def pause_length_auto_changed(self):
        if self.pause_length_auto.get():
            App.settings.set_audio_query_setting_parameter("pause_length", None)
        else:
            value = self.audio_param_controls["pause_length"]["scale"].get()
            App.settings.set_audio_query_setting_parameter("pause_length", value)

        self.update_pause_length_control_state()
        self.update_audio_param_label("pause_length")
        App.settings.save()

    def update_pause_length_control_state(self):
        state = tk.DISABLED if self.pause_length_auto.get() else tk.NORMAL
        self.audio_param_controls["pause_length"]["scale"].config(state=state)

    def update_audio_param_label(self, name):
        control = self.audio_param_controls[name]
        if name == "pause_length" and self.pause_length_auto.get():
            control["value_label"].config(text="自動")
            return

        value = control["scale"].get()
        control["value_label"].config(text=control["format"].format(value))

    # 開始ボタン押下イベントハンドラ
    def start_monitoring(self):
        if not self.monitoring:
            self.set_last_speech_text(pyperclip.paste())
            self.speech_queue = queue.Queue()
            self.stop_event.clear()
            self.monitoring_thread = threading.Thread(target=self.monitor_clipboard)
            self.speech_thread = threading.Thread(target=self.process_speech_queue)
            self.monitoring_thread.start()
            self.speech_thread.start()

            self.monitoring = True
            self.change_button_state()

    # 停止ボタン押下イベントハンドラ
    def stop_monitoring(self):
        if self.monitoring:
            self.stop_event.set()
            self.monitoring_thread.join()
            self.speech_thread.join()

    # リピートボタン押下イベントハンドラ
    def repeat_speech(self):
        text = pyperclip.paste()
        if text != "":
            self.speech_queue.put(text)

    # ボタンの状態を変更する
    def change_button_state(self):
        if self.monitoring:
            self.start_button.config(state=tk.DISABLED, image=self.icon_start_gray)
            self.stop_button.config(state=tk.NORMAL, image=self.icon_stop)
            self.repeat_button.config(state=tk.DISABLED, image=self.icon_repeat_gray)
        else:
            self.start_button.config(state=tk.NORMAL, image=self.icon_start)
            self.stop_button.config(state=tk.DISABLED, image=self.icon_stop_gray)
            self.repeat_button.config(state=tk.DISABLED, image=self.icon_repeat_gray)

    # ワーカースレッドからのメッセージを読み込む
    def read_monitoring_thread_message(self, q):
        try:
            signal = q.get_nowait()
            if signal == "speech started":
                self.on_speech_started()
            elif signal == "speech finished":
                self.on_speech_finished()
            elif signal == "monitoring thread terminated":
                self.on_monitoring_thread_terminated()
            elif signal == "voicevox api error":
                message = "VOICEVOX と通信できませんでした"
                messagebox.showerror(f"{APP_NAME}", message)
            elif signal == "unexpected error":
                message = "予期しない例外が発生しました"
                messagebox.showerror(f"{APP_NAME}", message)

            self.root.after(100, self.read_monitoring_thread_message, q)
        except queue.Empty:
            self.root.after(100, self.read_monitoring_thread_message, q)

    # ワーカースレッドで読み上げが開始された時に呼び出されるイベントハンドラ
    def on_speech_started(self):
        self.repeat_button.config(state=tk.DISABLED, image=self.icon_repeat_gray)

    # ワーカースレッドで読み上げが終了した時に呼び出されるイベントハンドラ
    def on_speech_finished(self):
        if self.monitoring:
            self.repeat_button.config(state=tk.NORMAL, image=self.icon_repeat)

    # ワーカースレッドが終了した時に呼び出されるイベントハンドラ
    def on_monitoring_thread_terminated(self):
        self.repeat_button.config(state=tk.DISABLED, image=self.icon_repeat_gray)
        self.monitoring = False
        self.change_button_state()

    # 最後に読み上げたテキストを取得する
    def get_last_speech_text(self):
        with self.lock:
            return self.last_speech_text
        
    # 最後に読み上げたテキストを設定する
    def set_last_speech_text(self, text):
        with self.lock:
            self.last_speech_text = text

    # クリップボードを監視する（ワーカースレッド）    
    def monitor_clipboard(self):
        try:
            while not self.stop_event.is_set():
                text = pyperclip.paste()
                if text != "" and text != self.get_last_speech_text():
                    self.set_last_speech_text(text)
                    self.speech_queue.put(text)
                time.sleep(0.1)
        except Exception as err:
            self.queue.put("unexpected error")
            self.stop_event.set()
            print(err)

    # 読み上げキューを処理する（ワーカースレッド）
    def process_speech_queue(self):
        try:
            while not self.stop_event.is_set():
                try:
                    text = self.speech_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                self.queue.put("speech started")
                lines = text.splitlines()
                for line in lines:
                    if not self.stop_event.is_set():
                        self.process_line(line)
                    else:
                        break
                self.speech_queue.task_done()
                self.queue.put("speech finished")
                print()
        except requests.exceptions.RequestException as err:
            self.queue.put("voicevox api error")
            self.stop_event.set()
            print(err)
        except Exception as err:
            self.queue.put("unexpected error")
            self.stop_event.set()
            print(err)
        finally:
            self.queue.put("monitoring thread terminated")
    
    # １行を処理する
    def process_line(self, line):
        print(line)
        line = self.replace_text(line)
        line = line.strip("\r\n-　 ")
        if line != "":
            sentences = line.split("。")
            for sentence in sentences:
                if not self.stop_event.is_set():
                    self.text_to_speech(
                        sentence, App.settings.get_speaker_id(),
                        App.settings.get_audio_query_parameters())
                else:
                    break
        else:
            time.sleep(0.2 / App.settings.get_speed_scale())

    # テキストを置換する
    def replace_text(self, text):
        for item in App.settings.get_replacements():
            pattern = item["pattern"]
            replacement = item["replacement"]
            text = re.sub(pattern, replacement, text)
        return text

    # テキストを読み上げる
    def text_to_speech(self, text, speaker_id, audio_query_parameters):
        query_json = VoicevoxAPI.audio_query(text, speaker_id)
        for key, value in audio_query_parameters.items():
            if key in query_json:
                query_json[key] = value
        wave_data = VoicevoxAPI.synthesis(query_json, speaker_id)
        self.play_sound(wave_data)

    # 音声データを再生する
    def play_sound(self, wave_data):
        wave_file = wave.open(io.BytesIO(wave_data), 'rb')
        audio = pyaudio.PyAudio()

        try:
            format = audio.get_format_from_width(wave_file.getsampwidth())

            stream = audio.open(
                format=format,
                channels=wave_file.getnchannels(),
                rate=wave_file.getframerate(),
                output=True)

            data = wave_file.readframes(1024)
            while data != b'':
                if self.stop_event.is_set():
                    break
                stream.write(data)
                data = wave_file.readframes(1024)
            time.sleep(0.2)
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()            
