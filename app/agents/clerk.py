from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from ..config import ROOT, load_config
from ..tools import ToolResult, execute_tool, is_destructive


CONSENT_LOG = ROOT / "logs" / "consent.log"
AUTONOMY_TOKEN_FILE = ROOT / "data" / "autonomy_token.txt"


@dataclass
class ClerkResult:
    ok: bool
    detail: str
    tool_result: ToolResult


class Clerk:
    """Executes tools under Bathy's supervision.

    Enforces safety_mode and allowed_tools from config. Destructive actions
    can require an explicit consent token or the presence of an autonomy
    token file on disk.
    """

    def __init__(self) -> None:
        self.cfg = load_config()

    def _is_allowed(self, name: str) -> bool:
        allowed = self.cfg.get("allowed_tools", [])
        return name in allowed

    def _safety_mode(self) -> str:
        return self.cfg.get("safety_mode", "interactive")

    def _log_consent(self, entry: Dict[str, Any]) -> None:
        CONSENT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with CONSENT_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _has_autonomy_token(self) -> bool:
        return AUTONOMY_TOKEN_FILE.exists()

    def execute(self, name: str, args: Dict[str, Any], consent_token: str | None = None) -> ClerkResult:
        mode = self._safety_mode()
        destructive = is_destructive(name)

        if not self._is_allowed(name):
            return ClerkResult(False, f"Tool '{name}' is not in allowed_tools.", ToolResult(name, False, "blocked", {}))

        if mode == "read-only" and destructive:
            return ClerkResult(False, f"Safety mode is read-only; '{name}' is destructive.", ToolResult(name, False, "blocked", {}))

        if mode == "interactive" and destructive:
            if not consent_token:
                return ClerkResult(
                    False,
                    f"Tool '{name}' requires explicit consent_token in interactive mode.",
                    ToolResult(name, False, "consent_required", {}),
                )
            self._log_consent({"tool": name, "args": list(args.keys()), "consent_token": "***"})

        if mode == "autonomous" and destructive:
            if not self._has_autonomy_token():
                return ClerkResult(
                    False,
                    "Autonomous mode requires autonomy_token.txt in data/; destructive tools are blocked.",
                    ToolResult(name, False, "autonomy_token_missing", {}),
                )

        result = execute_tool(name, args)
        ok = result.ok
        detail = result.detail
        return ClerkResult(ok, detail, result)
