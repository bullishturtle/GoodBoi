from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .config import ROOT, load_config
from .logging_utils import get_logger

LOG_DIR = ROOT / "logs"
ACTIONS_LOG = LOG_DIR / "actions.log"
TOOLS_REGISTRY_PATH = ROOT / "data" / "tools_registry.json"

log = get_logger(__name__)

os.makedirs(LOG_DIR, exist_ok=True)


@dataclass
class ToolResult:
    name: str
    ok: bool
    detail: str
    data: Dict[str, Any]


SAFE_SUBPROCESS_WHITELIST = {"dir", "type", "python", "pip", "git", "pytest", "ffmpeg"}


def _log_action(entry: Dict[str, Any]) -> None:
    entry["timestamp"] = datetime.utcnow().isoformat() + "Z"
    ACTIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ACTIONS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# --- Tool implementations ---


def read_file(path: str) -> ToolResult:
    p = (ROOT / path) if not os.path.isabs(path) else Path(path)
    try:
        text = p.read_text(encoding="utf-8")
        detail = f"Read {len(text)} characters from {p}"
        ok = True
        data = {"path": str(p), "content": text}
    except Exception as e:  # pragma: no cover - filesystem errors
        detail = f"read_file failed: {e}"
        ok = False
        data = {"path": str(p)}
    _log_action({"tool": "read_file", "ok": ok, "detail": detail, "path": str(p)})
    return ToolResult("read_file", ok, detail, data)


def _make_backup(path: Path) -> str:
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_dir = ROOT / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{path.name}.{ts}.bak"
    if path.exists():
        shutil.copy2(path, backup_path)
    return str(backup_path)


def write_file(path: str, content: str) -> ToolResult:
    p = (ROOT / path) if not os.path.isabs(path) else Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    backup_path = _make_backup(p)
    try:
        p.write_text(content, encoding="utf-8")
        detail = f"Wrote {len(content)} characters to {p} (backup: {backup_path})"
        ok = True
    except Exception as e:  # pragma: no cover
        detail = f"write_file failed: {e} (backup: {backup_path})"
        ok = False
    _log_action({"tool": "write_file", "ok": ok, "detail": detail, "path": str(p), "backup": backup_path})
    return ToolResult("write_file", ok, detail, {"path": str(p), "backup": backup_path})


def run_subprocess(command: str) -> ToolResult:
    # Very conservative: only allow commands whose first token is whitelisted.
    tokens = command.strip().split()
    if not tokens:
        return ToolResult("run_subprocess", False, "Empty command", {"command": command})

    base = tokens[0].lower()
    if base not in SAFE_SUBPROCESS_WHITELIST:
        detail = f"Command '{base}' is not in whitelist."
        _log_action({"tool": "run_subprocess", "ok": False, "detail": detail, "command": command})
        return ToolResult("run_subprocess", False, detail, {"command": command})

    try:
        proc = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        ok = proc.returncode == 0
        detail = f"Completed with return code {proc.returncode}"
        data = {
            "command": command,
            "stdout": proc.stdout[:4000],
            "stderr": proc.stderr[:4000],
        }
    except Exception as e:  # pragma: no cover
        ok = False
        detail = f"run_subprocess failed: {e}"
        data = {"command": command}

    _log_action({"tool": "run_subprocess", "ok": ok, "detail": detail, "command": command})
    return ToolResult("run_subprocess", ok, detail, data)


def open_url(url: str) -> ToolResult:
    # Do not actually open a browser here; just log and return.
    detail = f"Request to open URL: {url}"
    _log_action({"tool": "open_url", "ok": True, "detail": detail, "url": url})
    return ToolResult("open_url", True, detail, {"url": url})


def send_email_stub(to: str, subject: str, body: str) -> ToolResult:
    # Placeholder: real SMTP wiring would be configured later.
    preview = textwrap.shorten(body, width=200)
    detail = f"Email stub: to={to}, subject={subject}, body_preview={preview}"
    _log_action({"tool": "send_email", "ok": True, "detail": detail, "to": to, "subject": subject})
    return ToolResult("send_email", True, detail, {"to": to, "subject": subject})


def open_path(path: str) -> ToolResult:
    """Open a file or folder using the OS default handler.

    On Windows this uses os.startfile; on other platforms it falls back to
    xdg-open / open. This is considered destructive (it changes system state),
    so it is guarded by Clerk's safety rules.
    """

    p = (ROOT / path) if not os.path.isabs(path) else Path(path)
    try:
        if os.name == "nt":
            os.startfile(str(p))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(p)])
        else:
            subprocess.Popen(["xdg-open", str(p)])
        detail = f"Opened {p} via OS handler"
        ok = True
    except Exception as e:  # pragma: no cover
        detail = f"open_path failed: {e}"
        ok = False
    _log_action({"tool": "open_path", "ok": ok, "detail": detail, "path": str(p)})
    return ToolResult("open_path", ok, detail, {"path": str(p)})


def organize_downloads(root: str | None = None) -> ToolResult:
    """Organize a Downloads folder by file extension.

    Files are moved into subfolders like `Images/`, `Video/`, `Docs/`, `Other/`.
    This is intentionally simple and reversible (standard moves only).
    """

    cfg = load_config()
    if root is None:
        # Allow override from config; otherwise default to OS Downloads.
        root = cfg.get("downloads_dir") or str(Path.home() / "Downloads")
    base = Path(root)
    if not base.exists():
        detail = f"Downloads directory not found: {base}"
        _log_action({"tool": "organize_downloads", "ok": False, "detail": detail, "root": str(base)})
        return ToolResult("organize_downloads", False, detail, {"root": str(base)})

    mapping = {
        "Images": {".png", ".jpg", ".jpeg", ".gif", ".webp"},
        "Video": {".mp4", ".mov", ".mkv", ".avi"},
        "Audio": {".mp3", ".wav", ".flac", ".m4a"},
        "Docs": {".pdf", ".docx", ".pptx", ".xlsx", ".txt", ".md"},
    }

    moved: List[Dict[str, str]] = []
    for item in base.iterdir():
        if not item.is_file():
            continue
        ext = item.suffix.lower()
        target_dir_name = None
        for name, exts in mapping.items():
            if ext in exts:
                target_dir_name = name
                break
        if target_dir_name is None:
            target_dir_name = "Other"
        target_dir = base / target_dir_name
        target_dir.mkdir(exist_ok=True)
        target_path = target_dir / item.name
        try:
            shutil.move(str(item), target_path)
            moved.append({"from": str(item), "to": str(target_path)})
        except Exception:
            continue

    detail = f"Organized {len(moved)} file(s) in {base}"
    _log_action({"tool": "organize_downloads", "ok": True, "detail": detail, "root": str(base), "moved": moved})
    return ToolResult("organize_downloads", True, detail, {"root": str(base), "moved": moved})


def tail_logs(directory: str, pattern: str = "*.log", lines: int = 200) -> ToolResult:
    """Return the tail of the latest log file in a directory.

    This is a generic helper for app-specific diagnostics (e.g. Apex logs).
    """

    base = (ROOT / directory) if not os.path.isabs(directory) else Path(directory)
    if not base.exists():
        detail = f"Log directory not found: {base}"
        _log_action({"tool": "tail_logs", "ok": False, "detail": detail, "directory": str(base)})
        return ToolResult("tail_logs", False, detail, {"directory": str(base)})

    candidates = sorted(base.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        detail = f"No log files matching {pattern} in {base}"
        _log_action({"tool": "tail_logs", "ok": False, "detail": detail, "directory": str(base)})
        return ToolResult("tail_logs", False, detail, {"directory": str(base)})

    latest = candidates[0]
    try:
        text = latest.read_text(encoding="utf-8", errors="ignore")
        tail = "\n".join(text.splitlines()[-lines:])
        detail = f"Read tail of {latest} ({lines} lines)"
        ok = True
        data = {"path": str(latest), "tail": tail}
    except Exception as e:  # pragma: no cover
        detail = f"tail_logs failed: {e}"
        ok = False
        data = {"path": str(latest)}

    _log_action({"tool": "tail_logs", "ok": ok, "detail": detail, "directory": str(base), "path": str(latest)})
    return ToolResult("tail_logs", ok, detail, data)


TOOL_REGISTRY = {
    "read_file": {"func": read_file, "destructive": False},
    "write_file": {"func": write_file, "destructive": True},
    "run_subprocess": {"func": run_subprocess, "destructive": True},
    "open_url": {"func": open_url, "destructive": False},
    "send_email": {"func": send_email_stub, "destructive": False},
    "open_path": {"func": open_path, "destructive": True},
    "organize_downloads": {"func": organize_downloads, "destructive": True},
    "tail_logs": {"func": tail_logs, "destructive": False},
}


def _load_dynamic_tools() -> None:
    """Load additional tool definitions from data/tools_registry.json.

    Dynamic tools are intentionally constrained: right now we only support
    wrapping whitelisted subprocess commands. This keeps the surface area small
    while still letting Bathy grow new "skills" over time by editing a single
    JSON file.
    """

    if not TOOLS_REGISTRY_PATH.exists():
        return
    try:
        raw = json.loads(TOOLS_REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception as e:  # pragma: no cover
        log.error("Failed to load tools_registry.json: %s", e)
        return

    for tool in raw.get("tools", []):
        try:
            name = tool["name"]
            kind = tool.get("kind", "subprocess")
            destructive = bool(tool.get("destructive", False))
            if kind != "subprocess":
                continue

            command_template = tool.get("command_template")
            if not command_template:
                continue

            def make_func(template: str):
                def _fn(args: Dict[str, Any]) -> ToolResult:
                    # Simple template expansion: "{arg}" placeholders replaced
                    # from the args dict. This still flows through the
                    # run_subprocess safety checks.
                    try:
                        cmd = template.format(**args)
                    except Exception as e:  # pragma: no cover
                        return ToolResult(name, False, f"Template error: {e}", {"template": template})
                    inner = run_subprocess(cmd)
                    return ToolResult(name, inner.ok, inner.detail, inner.data)

                return _fn

            TOOL_REGISTRY[name] = {"func": make_func(command_template), "destructive": destructive}
        except Exception as e:  # pragma: no cover
            log.error("Error while registering dynamic tool: %s", e)


# Load dynamic tools at import time so they are visible to the Clerk.
_load_dynamic_tools()


def execute_tool(name: str, args: Dict[str, Any]) -> ToolResult:
    meta = TOOL_REGISTRY.get(name)
    if not meta:
        return ToolResult(name, False, f"Unknown tool: {name}", {})

    func = meta["func"]
    # Simple arg passing; we keep signatures small on purpose.
    try:
        if name == "read_file":
            return func(args["path"])
        if name == "write_file":
            return func(args["path"], args.get("content", ""))
        if name == "run_subprocess":
            return func(args["command"])
        if name == "open_url":
            return func(args["url"])
        if name == "send_email":
            return func(args["to"], args.get("subject", ""), args.get("body", ""))
        if name == "open_path":
            return func(args["path"])
        if name == "organize_downloads":
            return func(args.get("root"))
        if name == "tail_logs":
            return func(args["directory"], args.get("pattern", "*.log"), int(args.get("lines", 200)))
    except KeyError as e:
        return ToolResult(name, False, f"Missing argument: {e}", {})

    return ToolResult(name, False, "Unsupported tool invocation pattern", {})


def is_destructive(name: str) -> bool:
    meta = TOOL_REGISTRY.get(name)
    return bool(meta and meta.get("destructive"))
