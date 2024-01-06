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
    # コンストラクタ
    def __init__(self, app: Application):
        global App
        App = app

        self.monitoring = False
        self.stop_event = threading.Event()
        self.monitoring_thread = None
        self.queue = queue.Queue()
        self.last_speech_text = ""
        self.lock = threading.Lock()

        self.root = tk.Tk()
        window_width = 250
        window_height = 124
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

    # 終了処理
    def terminate(self):
        if self.monitoring:
            self.stop_event.set()
            self.monitoring_thread.join()

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

    # ウィジェットを配置する
    def layout(self):
        self.speaker_combo.grid(row=0, column=0, padx=5, pady=5, columnspan=8, sticky="w")
        self.speed_label.grid(row=1, column=0, padx=5, pady=5, columnspan=2, sticky="w")
        self.speed_scale.grid(row=1, column=2, padx=5, pady=5, columnspan=6, sticky="w")
        self.start_button.grid(row=2, column=0, padx=5, pady=5, columnspan=3, sticky="w")
        self.stop_button.grid(row=2, column=3, padx=5, pady=5, columnspan=3, sticky="w")
        self.repeat_button.grid(row=2, column=6, padx=5, pady=5, columnspan=2, sticky="w")
        self.change_button_state()

    # 話者ドロップダウンリストの変更イベントハンドラ
    def speaker_changed(self, evnet):
        current = self.speaker_combo.current()
        App.settings.set_speaker_id(App.speakers[current].id)
        App.settings.save()

    # 話速ラベルの表示を更新する
    def update_speed_label(self, value):
        self.speed_label.config(text=f"話速：{float(value):.1f}")

    # 話速スケールの変更イベントハンドラ
    def speed_scale_changed(self, event):
        speed_scale = self.speed_scale.get()
        App.settings.set_speed_scale(speed_scale)
        App.settings.save()

    # 開始ボタン押下イベントハンドラ
    def start_monitoring(self):
        if not self.monitoring:
            pyperclip.copy("")
            self.stop_event.clear()
            self.monitoring_thread = threading.Thread(target=self.monitor_clipboard)
            self.monitoring_thread.start()

            self.monitoring = True
            self.change_button_state()

    # 停止ボタン押下イベントハンドラ
    def stop_monitoring(self):
        if self.monitoring:
            self.stop_event.set()
            self.monitoring_thread.join()

    # リピートボタン押下イベントハンドラ
    def repeat_speech(self):
        self.set_last_speech_text("")

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
            self.set_last_speech_text("")
            while not self.stop_event.is_set():
                text = pyperclip.paste()
                if text != "" and text != self.get_last_speech_text():
                    self.queue.put("speech started")
                    lines = text.splitlines()
                    for line in lines:
                        if not self.stop_event.is_set():
                            self.process_line(line)
                    self.set_last_speech_text(text)
                    self.queue.put("speech finished")
                    print()
                time.sleep(0.5)
        except requests.exceptions.RequestException as err:
            self.queue.put("voicevox api error")
            print(err)
        except Exception as err:
            self.queue.put("unexpected error")
            print(err)
        finally:
            self.queue.put("monitoring thread terminated")
    
    # １行を処理する
    def process_line(self, line):
        print(line)
        line = line.strip("\r\n-　 ")
        if line != "":
            sentences = line.split("。")
            for sentence in sentences:
                if not self.stop_event.is_set():
                    self.text_to_speech(
                        sentence, App.settings.get_speaker_id(),
                        App.settings.get_speed_scale(), App.settings.get_pitch_scale())
                else:
                    break
        else:
            time.sleep(0.2 / App.settings.get_speed_scale())

    # テキストを読み上げる
    def text_to_speech(self, text, speaker_id, speed_scale, pitch_scale):
        query_json = VoicevoxAPI.audio_query(text, speaker_id)
        query_json["speedScale"] = speed_scale
        query_json["pitchScale"] = pitch_scale
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
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()            
