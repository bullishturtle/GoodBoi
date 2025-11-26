"""User profile and self-learning manager for GoodBoy.AI.

This module is deliberately simple and transparent: it stores preferences and
usage statistics in JSON so that other agents (especially the Overseer) can
inspect how Bathy is used and propose improvements.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from .config import ROOT
from .logging_utils import get_logger

log = get_logger(__name__)

DATA_DIR = ROOT / "data"
PROFILE_PATH = DATA_DIR / "user_profile.json"
EXPERIENCE_LOG_PATH = DATA_DIR / "experience_log.jsonl"


@dataclass
class UserProfile:
    """High-level preferences and usage stats for the primary owner.

    This is *not* a training dataset; it's a compact summary that other agents
    can read to adapt behavior (e.g., preferred tone, favorite tools).
    """

    owner_name: str = "Lando"
    preferred_tone: str = "concise-strategic"
    default_agent: str = "writer"  # which advisor Bathy favors when ambiguous
    chats_total: int = 0
    tools_total: int = 0
    tools_successful: int = 0
    last_seen_iso: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "UserProfile":
        base = UserProfile()
        for k, v in data.items():
            if hasattr(base, k):
                setattr(base, k, v)
        return base


class UserProfileStore:
    """Handles loading/updating the profile and appending experience logs."""

    def __init__(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._profile = self._load()

    # --- Persistence ---------------------------------------------------------

    def _load(self) -> UserProfile:
        if not PROFILE_PATH.exists():
            profile = UserProfile()
            self._save(profile)
            return profile
        try:
            raw = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
            return UserProfile.from_dict(raw)
        except Exception as e:  # pragma: no cover
            log.error("Failed to load user_profile.json: %s", e)
            profile = UserProfile()
            self._save(profile)
            return profile

    def _save(self, profile: UserProfile) -> None:
        PROFILE_PATH.write_text(json.dumps(profile.to_dict(), indent=2), encoding="utf-8")

    def snapshot(self) -> UserProfile:
        return self._profile

    # --- Learning hooks ------------------------------------------------------

    def record_chat(self, message: str, reply: str) -> None:
        self._profile.chats_total += 1
        self._profile.last_seen_iso = datetime.now(timezone.utc).isoformat()
        self._save(self._profile)

        entry = {
            "kind": "chat",
            "ts": datetime.now(timezone.utc).isoformat(),
            "message": message,
            "reply": reply,
        }
        with EXPERIENCE_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def record_tool(self, name: str, ok: bool, detail: str) -> None:
        self._profile.tools_total += 1
        if ok:
            self._profile.tools_successful += 1
        self._profile.last_seen_iso = datetime.now(timezone.utc).isoformat()
        self._save(self._profile)

        entry = {
            "kind": "tool",
            "ts": datetime.now(timezone.utc).isoformat(),
            "tool": name,
            "ok": ok,
            "detail": detail,
        }
        with EXPERIENCE_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# Singleton-style accessor so the rest of the app can use one store.
_store: UserProfileStore | None = None


def get_store() -> UserProfileStore:
    global _store
    if _store is None:
        _store = UserProfileStore()
    return _store
