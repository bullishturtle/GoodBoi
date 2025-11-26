from __future__ import annotations

import threading
from pathlib import Path
from typing import Optional

from .config import load_config, ROOT

try:
    from gpt4all import GPT4All
except Exception as e:  # pragma: no cover
    GPT4All = None  # type: ignore


class ModelBackend:
    """Thin wrapper around GPT4All for local GGUF models.

    For now we use GPT4All instead of llama-cpp-python on Windows to avoid
    compiler issues while still running Qwen/TinyLlama locally.
    """

    _instance_lock = threading.Lock()
    _instance: Optional["ModelBackend"] = None

    def __init__(self) -> None:
        cfg = load_config()
        self.config = cfg
        model_rel = cfg.get("model_path") or "models/qwen2.5-7b-instruct-q5_k_m-00001-of-00002.gguf"
        self.model_path = (ROOT / model_rel).resolve()
        if GPT4All is None:
            raise RuntimeError("gpt4all is not installed; install with `pip install gpt4all` in the venv.")

        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        # GPT4All expects model name and optional model_path directory
        self._model = GPT4All(self.model_path.name, model_path=str(self.model_path.parent))

    @classmethod
    def instance(cls) -> "ModelBackend":
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def generate(self, prompt: str, max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> str:
        cfg = self.config
        max_toks = max_tokens or int(cfg.get("max_tokens", 512))
        temp = float(temperature if temperature is not None else cfg.get("temperature", 0.6))

        with self._model.chat_session():
            out = self._model.generate(prompt, max_tokens=max_toks, temp=temp)
        return out.strip()
