"""Voice interaction scaffolding for GoodBoy.AI.

This module is intentionally conservative: it provides wake-word listening and
text-to-speech hooks *if* the relevant libraries are installed, but the rest of
Bathy can run without them. Configuration is driven by GoodBoy_config.json.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .config import load_config
from .logging_utils import get_logger

log = get_logger(__name__)

try:  # Optional dependencies
    import sounddevice as sd  # type: ignore
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover - optional
    sd = None  # type: ignore
    np = None  # type: ignore

try:
    import pyttsx3  # type: ignore
except Exception:  # pragma: no cover - optional
    pyttsx3 = None  # type: ignore

try:  # Optional Whisper STT
    import whisper  # type: ignore
except Exception:  # pragma: no cover - optional
    whisper = None  # type: ignore


@dataclass
class VoiceConfig:
    enabled: bool
    wake_word: str
    input_device: Optional[str]
    output_device: Optional[str]
    stt_backend: str
    tts_backend: str


def load_voice_config() -> VoiceConfig:
    cfg = load_config().get("voice", {})
    return VoiceConfig(
        enabled=bool(cfg.get("enabled", False)),
        wake_word=str(cfg.get("wake_word", "hey bathy")),
        input_device=cfg.get("input_device"),
        output_device=cfg.get("output_device"),
        stt_backend=str(cfg.get("stt_backend", "whisper_local")),
        tts_backend=str(cfg.get("tts_backend", "pyttsx3")),
    )


class WakeWordListener:
    """Very small wake-word listener.

    For now this is *phoneme-agnostic* and simply looks for audio energy above
    a threshold for a minimum duration. It is designed to be replaced later by
    a dedicated wake-word model such as `openwakeword` or Porcupine.
    """

    def __init__(self, voice_cfg: VoiceConfig, energy_threshold: float = 0.02) -> None:
        self.voice_cfg = voice_cfg
        self.energy_threshold = energy_threshold
        self._check_libs()

    def _check_libs(self) -> None:
        if sd is None or np is None:
            raise RuntimeError(
                "sounddevice and numpy are required for voice input but are not installed. "
                "Install them in the venv to enable wake-word listening."
            )

    def wait_for_wake(self, seconds: int = 10) -> bool:
        """Block and listen for any loud-enough sound.

        Returns True if sound activity is detected within the window.
        """

        if not self.voice_cfg.enabled:
            return False

        samplerate = 16000
        duration = seconds
        log.info("WakeWordListener listening", extra={"seconds": seconds})

        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
        sd.wait()
        energy = float(np.abs(recording).mean())  # type: ignore[arg-type]
        log.info("WakeWordListener energy", extra={"energy": energy})
        return energy > self.energy_threshold


class TextToSpeech:
    """Thin wrapper around pyttsx3 (if available)."""

    def __init__(self, voice_cfg: VoiceConfig) -> None:
        self.voice_cfg = voice_cfg
        self.engine = None
        if voice_cfg.tts_backend == "pyttsx3" and pyttsx3 is not None:
            try:
                self.engine = pyttsx3.init()
            except Exception as e:  # pragma: no cover
                log.error("Failed to init pyttsx3: %s", e)
                self.engine = None

    def speak(self, text: str) -> None:
        if not self.voice_cfg.enabled:
            return
        if not self.engine:
            log.warning("TTS requested but engine is not available")
            return
        log.info("Speaking response", extra={"chars": len(text)})
        self.engine.say(text)
        self.engine.runAndWait()


class SpeechToText:
    """Whisper-based speech-to-text (if available).

    Records a short audio snippet from the microphone and runs local Whisper
    transcription. This requires sounddevice, numpy, and the `whisper` package.
    """

    def __init__(self, voice_cfg: VoiceConfig) -> None:
        self.voice_cfg = voice_cfg
        self.model = None
        if (
            voice_cfg.stt_backend == "whisper_local"
            and whisper is not None
            and sd is not None
            and np is not None
        ):
            try:
                # "base" is a good balance between speed and accuracy.
                self.model = whisper.load_model("base")
                log.info("Whisper STT model loaded", extra={"backend": "whisper_local"})
            except Exception as e:  # pragma: no cover
                log.error("Failed to load Whisper model: %s", e)
                self.model = None

    def transcribe_once(self, seconds: int = 8) -> str:
        """Record from mic for a few seconds and return recognized text.

        Returns an empty string on failure.
        """

        if not self.model or not self.voice_cfg.enabled:
            return ""
        if sd is None or np is None:
            return ""

        samplerate = 16000
        log.info("Recording audio for STT", extra={"seconds": seconds})
        try:
            recording = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=1)
            sd.wait()
        except Exception as e:  # pragma: no cover
            log.error("Error recording audio for STT: %s", e)
            return ""

        audio = recording.flatten().astype("float32")  # type: ignore[arg-type]
        try:
            result = self.model.transcribe(audio)
            text = str(result.get("text", "")).strip()
            log.info("STT transcription complete", extra={"chars": len(text)})
            return text
        except Exception as e:  # pragma: no cover
            log.error("Error during Whisper transcription: %s", e)
            return ""


def build_voice_stack() -> Dict[str, Any]:
    """Factory that builds a coherent voice stack based on config.

    Returns a dict with keys: voice_cfg, wake_listener, tts.
    Some entries may be None if libraries are unavailable; callers should
    handle this gracefully.
    """

    voice_cfg = load_voice_config()
    if not voice_cfg.enabled:
        return {"voice_cfg": voice_cfg, "wake_listener": None, "tts": None, "stt": None}

    wake_listener: Optional[WakeWordListener]
    tts: Optional[TextToSpeech]
    stt: Optional[SpeechToText]

    try:
        wake_listener = WakeWordListener(voice_cfg)
    except Exception as e:  # pragma: no cover
        log.error("Wake listener unavailable: %s", e)
        wake_listener = None

    tts = TextToSpeech(voice_cfg)
    stt = SpeechToText(voice_cfg)
    if stt.model is None:
        stt = None
    return {"voice_cfg": voice_cfg, "wake_listener": wake_listener, "tts": tts, "stt": stt}
