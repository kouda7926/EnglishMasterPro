#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sound & TTS System for EnglishMaster Pro"""

import threading

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    from kivy.core.audio import SoundLoader
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

import os
import tempfile


class SoundSystem:
    def __init__(self):
        self.cache = {}
        self.temp_dir = tempfile.mkdtemp()
        self.enabled = True
        self.volume = 1.0

    def speak(self, text, lang="en"):
        if not self.enabled:
            return
        threading.Thread(target=self._speak_thread, args=(text, lang), daemon=True).start()

    def _speak_thread(self, text, lang):
        try:
            key = f"{lang}:{text}"
            if key in self.cache:
                path = self.cache[key]
            elif GTTS_AVAILABLE:
                tts = gTTS(text=text, lang=lang)
                path = os.path.join(self.temp_dir, f"{hash(key)}.mp3")
                tts.save(path)
                self.cache[key] = path
            else:
                return
            if AUDIO_AVAILABLE:
                sound = SoundLoader.load(path)
                if sound:
                    sound.volume = self.volume
                    sound.play()
        except Exception:
            pass

    def speak_english(self, text):
        self.speak(text, "en")

    def speak_arabic(self, text):
        self.speak(text, "ar")

    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled

    def clear_cache(self):
        for path in self.cache.values():
            try:
                os.remove(path)
            except OSError:
                pass
        self.cache.clear()
