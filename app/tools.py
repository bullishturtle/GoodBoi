"""Tool definitions for agent actions."""
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass


@dataclass
class ToolResult:
    """Result from tool execution."""
    success: bool
    output: Any
    error: Optional[str] = None


class ToolRegistry:
    """Registry for all available tools."""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """Register built-in tools."""
        self.register("list_files", self._list_files, "List files in a directory")
        self.register("read_file", self._read_file, "Read contents of a file")
        self.register("write_file", self._write_file, "Write content to a file")
        self.register("run_command", self._run_command, "Run a shell command")
        self.register("search_files", self._search_files, "Search files by pattern")
        self.register("get_time", self._get_time, "Get current time")
        self.register("create_reminder", self._create_reminder, "Create a reminder")
        self.register("analyze_code", self._analyze_code, "Analyze code structure")
    
    def register(self, name: str, func: Callable, description: str):
        """Register a new tool."""
        self.tools[name] = {
            "func": func,
            "description": description
        }
    
    def execute(self, name: str, **kwargs) -> ToolResult:
        """Execute a tool by name."""
        if name not in self.tools:
            return ToolResult(success=False, output=None, error=f"Tool '{name}' not found")
        
        try:
            result = self.tools[name]["func"](**kwargs)
            return ToolResult(success=True, output=result)
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))
    
    def list_available(self) -> List[Dict[str, str]]:
        """List all available tools."""
        return [
            {"name": name, "description": info["description"]}
            for name, info in self.tools.items()
        ]
    
    # Built-in tool implementations
    def _list_files(self, path: str = ".", pattern: str = "*") -> List[str]:
        """List files in directory."""
        p = Path(path)
        if not p.exists():
            return []
        return [str(f) for f in p.glob(pattern)]
    
    def _read_file(self, path: str) -> str:
        """Read file contents."""
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    
    def _write_file(self, path: str, content: str) -> str:
        """Write content to file."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Wrote {len(content)} chars to {path}"
    
    def _run_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Run shell command (sandboxed)."""
        # Security: Block dangerous commands
        blocked = ["rm -rf", "format", "del /", "rmdir /s"]
        if any(b in command.lower() for b in blocked):
            return {"error": "Command blocked for security"}
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "stdout": result.stdout[:2000],
                "stderr": result.stderr[:500],
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
    
    def _search_files(self, directory: str, pattern: str, content: Optional[str] = None) -> List[Dict]:
        """Search files by name pattern and optionally content."""
        results = []
        p = Path(directory)
        
        for file in p.rglob(pattern):
            if file.is_file():
                entry = {"path": str(file), "size": file.stat().st_size}
                
                if content:
                    try:
                        text = file.read_text(encoding="utf-8", errors="ignore")
                        if content.lower() in text.lower():
                            entry["matches"] = True
                            results.append(entry)
                    except Exception:
                        pass
                else:
                    results.append(entry)
                
                if len(results) >= 50:
                    break
        
        return results
    
    def _get_time(self) -> Dict[str, str]:
        """Get current time info."""
        now = datetime.now()
        return {
            "datetime": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "weekday": now.strftime("%A")
        }
    
    def _create_reminder(self, message: str, time: str) -> Dict[str, str]:
        """Create a reminder (stored in memory)."""
        reminders_file = Path("memory/reminders.jsonl")
        reminders_file.parent.mkdir(exist_ok=True)
        
        reminder = {
            "id": f"rem_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "message": message,
            "due": time,
            "created": datetime.now().isoformat(),
            "status": "pending"
        }
        
        with open(reminders_file, "a") as f:
            f.write(json.dumps(reminder) + "\n")
        
        return {"status": "created", "reminder": reminder}
    
    def _analyze_code(self, path: str) -> Dict[str, Any]:
        """Analyze code file structure."""
        content = self._read_file(path)
        lines = content.split("\n")
        
        analysis = {
            "path": path,
            "lines": len(lines),
            "chars": len(content),
            "functions": [],
            "classes": [],
            "imports": []
        }
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("def "):
                name = stripped.split("(")[0].replace("def ", "")
                analysis["functions"].append({"name": name, "line": i + 1})
            elif stripped.startswith("class "):
                name = stripped.split("(")[0].split(":")[0].replace("class ", "")
                analysis["classes"].append({"name": name, "line": i + 1})
            elif stripped.startswith("import ") or stripped.startswith("from "):
                analysis["imports"].append(stripped)
        
        return analysis


# Global singleton
_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get or create the tool registry singleton."""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry
