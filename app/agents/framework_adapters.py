"""Optional adapters for external agent frameworks (CrewAI, AgentVerse).

These are thin wrappers so that GoodBoy.AI can interoperate with richer agent
frameworks without taking a hard dependency. If the corresponding packages are
not installed, the adapters simply report `available = False`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from ..logging_utils import get_logger

log = get_logger(__name__)


@dataclass
class FrameworkStatus:
    name: str
    available: bool
    version: str | None


class CrewAIAdapter:
    def __init__(self) -> None:
        try:
            import crewai  # type: ignore

            self._mod = crewai
            self.status = FrameworkStatus("crewai", True, getattr(crewai, "__version__", None))
        except Exception:  # pragma: no cover - optional
            self._mod = None
            self.status = FrameworkStatus("crewai", False, None)

    def is_available(self) -> bool:
        return self.status.available

    def describe(self) -> Dict[str, Any]:
        return self.status.__dict__


class AgentVerseAdapter:
    def __init__(self) -> None:
        try:
            import agentverse  # type: ignore

            self._mod = agentverse
            self.status = FrameworkStatus("agentverse", True, getattr(agentverse, "__version__", None))
        except Exception:  # pragma: no cover - optional
            self._mod = None
            self.status = FrameworkStatus("agentverse", False, None)

    def is_available(self) -> bool:
        return self.status.available

    def describe(self) -> Dict[str, Any]:
        return self.status.__dict__
