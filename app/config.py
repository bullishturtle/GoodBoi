import json
import os
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CONFIG_PATH = DATA_DIR / "GoodBoy_config.json"

# NOTE: This is the *schema* of defaults. Existing user configs are not overwritten;
# missing keys are simply read via .get() in the rest of the codebase.
DEFAULT_CONFIG: Dict[str, Any] = {
    "engine": "local",  # "local" or "cloud"
    "model_path": "models/qwen2.5-7b-instruct-q5_k_m-00001-of-00002.gguf",
    "small_model_path": "models/goodboy_small.gguf",
    "cloud_api_base": "http://127.0.0.1:8000",
    "cloud_model": "meta-llama-3-8b-instruct",
    "max_tokens": 512,
    "temperature": 0.6,
    "memory_backend": "chromadb",  # "chromadb" or "none"
    "safety_mode": "interactive",  # "read-only" | "interactive" | "autonomous"
    "admin_user": "lando",
    "allowed_tools": [
        "read_file",
        "write_file",
        "run_subprocess",
        "open_url",
        "send_email",
        "open_path",
        "organize_downloads",
        "tail_logs",
    ],
    "api_keys": {"openai": "", "anthropic": ""},
    # When true, each /chat API interaction is logged to disk and also offered
    # into the MemoryBackend as an embedding item when available.
    "memory_auto_ingest_from_api": True,
    # Voice interaction defaults; can be toggled off globally.
    "voice": {
        "enabled": False,
        "wake_word": "hey bathy",
        "input_device": None,  # OS default when None
        "output_device": None,
        # Speech-to-text + TTS backend identifiers for future wiring.
        "stt_backend": "whisper_local",  # or "none"
        "tts_backend": "pyttsx3",       # or "none"
    },
    # Automation / scheduler defaults.
    "automation": {
        # If true, the AutomationEngine will attempt to run due tasks when
        # /automation/run-due is called. External schedulers can simply ping
        # that endpoint.
        "enabled": True,
        # Upper bound on how many tasks we execute in a single run-due call.
        "max_parallel_tasks": 2,
        # When true, process_action_queue may automatically execute non-destructive
        # tool suggestions that Bathy generates, closing the loop from ideas to
        # safe actions. Default is False for human-in-the-loop.
        "auto_apply_actions_for_safe_tools": False,
    },
    # Optional convenience paths for app-specific helpers.
    "paths": {
        "downloads_dir": None,
        "logs_dir": None,
    },
}


def load_config() -> Dict[str, Any]:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
        return DEFAULT_CONFIG.copy()
    try:
        return json.loads(CONFIG_PATH.read_text())
    except Exception:
        # fallback to default but do not overwrite user file
        return DEFAULT_CONFIG.copy()
