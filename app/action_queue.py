"""Action queue for model-suggested follow-up steps.

This module collects SuggestedAction items from /chat responses and stores them
in an append-only JSONL log. Separate scripts can periodically process this
queue to execute safe actions, create automations, or add teachings.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List

from .config import ROOT
from .logging_utils import get_logger

log = get_logger(__name__)

DATA_DIR = ROOT / "data"
QUEUE_PATH = DATA_DIR / "action_queue.jsonl"


@dataclass
class QueuedAction:
    kind: str
    description: str
    tool_name: str | None
    tool_args: Dict[str, Any]
    source_message: str
    source_reply: str
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def enqueue_actions(actions: List[Dict[str, Any]], source_message: str, source_reply: str) -> int:
    """Append suggested actions to the queue.

    Returns the number of actions enqueued.
    """

    if not actions:
        return 0

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    count = 0
    with QUEUE_PATH.open("a", encoding="utf-8") as f:
        for a in actions:
            qa = QueuedAction(
                kind=str(a.get("kind", "note")),
                description=str(a.get("description", "")),
                tool_name=a.get("tool_name"),
                tool_args=a.get("tool_args") or {},
                source_message=source_message,
                source_reply=source_reply,
                created_at=now,
            )
            f.write(json.dumps(qa.to_dict(), ensure_ascii=False) + "\n")
            count += 1
    log.info("Enqueued suggested actions", extra={"count": count})
    return count
