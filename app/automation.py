"""Lightweight automation engine for GoodBoy.AI.

This module defines a JSON-backed task registry and a small scheduler that can
execute sequences of tool calls (via the Clerk safety layer). It is designed to
be driven either by the FastAPI layer or by external OS schedulers (Task
Scheduler / cron) that periodically call `run_due_tasks`.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from .config import ROOT, load_config
from .agents.clerk import Clerk, ClerkResult
from .logging_utils import get_logger

log = get_logger(__name__)

DATA_DIR = ROOT / "data"
TASKS_PATH = DATA_DIR / "automation_tasks.json"

ScheduleKind = Literal["once", "interval"]


@dataclass
class AutomationStep:
    """Single step in an automation task: a tool invocation."""

    tool: str
    args: Dict[str, Any]


@dataclass
class AutomationTask:
    """A scheduled task composed of one or more AutomationSteps.

    - id: stable identifier (string) so tasks can be updated/removed.
    - schedule: either a one-off run_at timestamp or a recurring interval.
    """

    id: str
    name: str
    enabled: bool = True
    kind: ScheduleKind = "interval"
    # For `kind == "once"`, next_run_at is the execution time (UTC ISO-8601).
    # For `kind == "interval"`, next_run_at is the next fire time and
    # interval_seconds controls the spacing between runs.
    next_run_at: Optional[str] = None
    interval_seconds: Optional[int] = None
    steps: List[AutomationStep] | None = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # dataclasses.asdict already converts nested dataclasses to dicts.
        return d

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "AutomationTask":
        steps = [AutomationStep(**s) for s in data.get("steps", [])]
        return AutomationTask(
            id=data["id"],
            name=data.get("name", data["id"]),
            enabled=bool(data.get("enabled", True)),
            kind=data.get("kind", "interval"),
            next_run_at=data.get("next_run_at"),
            interval_seconds=data.get("interval_seconds"),
            steps=steps,
        )


class AutomationEngine:
    """JSON-backed automation engine.

    Responsibilities:
    - Load/save tasks from `automation_tasks.json`.
    - Provide CRUD helpers for tasks.
    - Compute which tasks are due at a given time.
    - Execute tasks via the Clerk, respecting GoodBoy safety rules.
    """

    def __init__(self) -> None:
        self.cfg = load_config()
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.clerk = Clerk()
        self._tasks: Dict[str, AutomationTask] = {}
        self._load()

    # --- Persistence helpers -------------------------------------------------

    def _load(self) -> None:
        if not TASKS_PATH.exists():
            self._tasks = {}
            return
        try:
            raw = json.loads(TASKS_PATH.read_text(encoding="utf-8"))
        except Exception as e:  # pragma: no cover - corrupt file
            log.error("Failed to load automation tasks: %s", e)
            self._tasks = {}
            return
        items = raw.get("tasks", []) if isinstance(raw, dict) else []
        self._tasks = {}
        for item in items:
            try:
                task = AutomationTask.from_dict(item)
                self._tasks[task.id] = task
            except Exception as e:  # pragma: no cover
                log.error("Failed to parse task definition: %s", e)

    def _save(self) -> None:
        data = {"tasks": [t.to_dict() for t in self._tasks.values()]}
        TASKS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # --- Public API ----------------------------------------------------------

    def list_tasks(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self._tasks.values()]

    def upsert_task(self, task_data: Dict[str, Any]) -> AutomationTask:
        """Create or update a task from a dict payload.

        If `next_run_at` is omitted for interval tasks, schedule first run from
        now + interval.
        """

        task = AutomationTask.from_dict(task_data)
        now = datetime.now(timezone.utc)
        if task.kind == "interval" and task.interval_seconds and not task.next_run_at:
            task.next_run_at = (now + timedelta(seconds=task.interval_seconds)).isoformat()
        self._tasks[task.id] = task
        self._save()
        log.info("Automation task upserted", extra={"task_id": task.id, "name": task.name})
        return task

    def delete_task(self, task_id: str) -> bool:
        removed = self._tasks.pop(task_id, None) is not None
        if removed:
            self._save()
            log.info("Automation task deleted", extra={"task_id": task_id})
        return removed

    # --- Execution -----------------------------------------------------------

    def _parse_next_run(self, task: AutomationTask) -> Optional[datetime]:
        if not task.next_run_at:
            return None
        try:
            return datetime.fromisoformat(task.next_run_at)
        except Exception:  # pragma: no cover
            return None

    def _update_next_run(self, task: AutomationTask, now: datetime) -> None:
        if task.kind == "once":
            task.enabled = False
            task.next_run_at = None
            return
        if task.kind == "interval" and task.interval_seconds:
            task.next_run_at = (now + timedelta(seconds=task.interval_seconds)).isoformat()

    def run_due_tasks(self, now: Optional[datetime] = None) -> Dict[str, Any]:
        """Execute all tasks whose `next_run_at` is in the past.

        Returns a structured report of what was executed.
        """

        if now is None:
            now = datetime.now(timezone.utc)

        report: Dict[str, Any] = {"ran": [], "skipped": []}
        max_parallel = int(self.cfg.get("automation", {}).get("max_parallel_tasks", 2))
        remaining_slots = max_parallel

        for task in list(self._tasks.values()):
            nr = self._parse_next_run(task)
            if not task.enabled or nr is None:
                report["skipped"].append({"id": task.id, "reason": "disabled_or_unscheduled"})
                continue
            if nr > now:
                report["skipped"].append({"id": task.id, "reason": "not_due"})
                continue
            if remaining_slots <= 0:
                report["skipped"].append({"id": task.id, "reason": "parallelism_limit"})
                continue

            results: List[Dict[str, Any]] = []
            for step in task.steps or []:
                res: ClerkResult = self.clerk.execute(step.tool, step.args)
                results.append(
                    {
                        "tool": step.tool,
                        "ok": res.ok,
                        "detail": res.detail,
                        "result": res.tool_result.data,
                    }
                )

            self._update_next_run(task, now)
            report["ran"].append({"id": task.id, "name": task.name, "results": results})
            remaining_slots -= 1

        self._save()
        return report
