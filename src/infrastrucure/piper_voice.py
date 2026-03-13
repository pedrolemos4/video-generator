#!/usr/bin/env python3
"""
infrastructure/piper_voice.py
------------------------------
Enum of available Piper TTS voice models with correct HuggingFace download URLs.
"""

from enum import Enum


class PiperVoice(Enum):

    # value is (lang_code, speaker, quality)
    EN_US_LESSAC_MEDIUM = ("en_US", "lessac", "medium")
    EN_US_RYAN_MEDIUM = ("en_US", "ryan", "medium")
    EN_GB_ALAN_MEDIUM = ("en_GB", "alan", "medium")

    @property
    def model_name(self) -> str:
        lang, speaker, quality = self.value
        return f"{lang}-{speaker}-{quality}"

    @property
    def model_path(self) -> str:
        return f"/app/voices/{self.model_name}.onnx"

    @property
    def config_path(self) -> str:
        return f"/app/voices/{self.model_name}.onnx.json"

    @property
    def download_url(self) -> str:
        lang, speaker, quality = self.value
        lang_prefix = lang[:2].lower()  # en
        lang_region = lang[3:].upper()  # US
        base = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0"
        return f"{base}/{lang_prefix}/{lang_prefix}_{lang_region}/{speaker}/{quality}/{self.model_name}.onnx"

    @property
    def config_url(self) -> str:
        return self.download_url + ".json"
