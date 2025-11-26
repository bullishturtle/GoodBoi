from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from ..config import ROOT, load_config


STATUS_FILE = ROOT / "logs" / "janitor_status.json"


@dataclass
class JanitorReport:
    ok: bool
    summary: str
    details: Dict[str, Any]


class Janitor:
    """Health-check and self-diagnosis helper for GoodBoy.AI.

    Does not modify code; only inspects and reports.
    """

    def __init__(self) -> None:
        self.cfg = load_config()

    def _disk_usage(self, path: Path) -> Dict[str, Any]:
        total, used, free = shutil.disk_usage(path)
        return {"total": total, "used": used, "free": free}

    def run_checks(self) -> JanitorReport:
        model_path = ROOT / self.cfg.get("model_path", "")
        small_model_path = ROOT / self.cfg.get("small_model_path", "")
        issues = []

        if not model_path.exists():
            issues.append(f"Main model missing: {model_path}")
        if small_model_path and not small_model_path.exists():
            issues.append(f"Small model missing: {small_model_path}")

        disk = self._disk_usage(ROOT)
        if disk["free"] < 2 * 1024 * 1024 * 1024:  # <2GB
            issues.append("Low disk space (<2GB free)")

        logs_dir = ROOT / "logs"
        recent_logs = []
        if logs_dir.exists():
            for p in logs_dir.glob("*.log"):
                try:
                    text = p.read_text(encoding="utf-8", errors="ignore")
                    recent_logs.append({"file": str(p), "size": len(text)})
                except Exception:
                    continue

        ok = not issues
        summary = "System healthy" if ok else "Issues detected: " + "; ".join(issues)
        details: Dict[str, Any] = {
            "model_path": str(model_path),
            "small_model_path": str(small_model_path),
            "disk": disk,
            "issues": issues,
            "logs": recent_logs,
        }

        STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            import json

            STATUS_FILE.write_text(json.dumps({"ok": ok, "summary": summary, "details": details}, indent=2))
        except Exception:
            pass

        return JanitorReport(ok=ok, summary=summary, details=details)

    def last_status(self) -> Dict[str, Any]:
        if not STATUS_FILE.exists():
            rep = self.run_checks()
            return {"ok": rep.ok, "summary": rep.summary, "details": rep.details}
        import json

        try:
            return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
        except Exception:
            rep = self.run_checks()
            return {"ok": rep.ok, "summary": rep.summary, "details": rep.details}
