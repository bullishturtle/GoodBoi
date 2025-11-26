"""Teaching store for user-provided lessons and corrections.

This module lets the owner explicitly "teach" GoodBoy.AI by writing structured
lessons to disk. Lessons are also suitable for ingestion into the memory
backend or offline fine-tuning pipelines later.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import ROOT
from .logging_utils import get_logger

log = get_logger(__name__)

DATA_DIR = ROOT / "data"
LESSONS_PATH = DATA_DIR / "teachings.jsonl"


@dataclass
class Teaching:
    """A single owner-provided lesson.

    Fields are intentionally generic so they can cover corrections, new
    preferences, or domain-specific knowledge.
    """

    topic: str
    instruction: str
    tags: List[str]
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TeachingStore:
    def __init__(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.path = LESSONS_PATH

    def add_lesson(self, topic: str, instruction: str, tags: Optional[List[str]] = None) -> Teaching:
        lesson = Teaching(
            topic=topic,
            instruction=instruction,
            tags=tags or [],
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(lesson.to_dict(), ensure_ascii=False) + "\n")
        log.info("Teaching added", extra={"topic": topic, "tags": tags or []})
        return lesson

    def load_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        out: List[Dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except Exception:
                    continue
        if limit is not None:
            return out[-limit:]
        return out


_store: Optional[TeachingStore] = None


def get_store() -> TeachingStore:
    global _store
    if _store is None:
        _store = TeachingStore()
    return _store
