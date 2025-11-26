"""Alfred Agent - Scheduling & Administrative specialist."""
from app.agents.base import BaseAgent
from typing import Optional, Dict
from datetime import datetime
import json
from pathlib import Path


ALFRED_SYSTEM = """You are Alfred, the Scheduling & Administrative specialist in the GoodBoy.AI council.

Your responsibilities:
- Manage schedules, calendars, and appointments
- Draft and send communications (emails, messages)
- Handle logistics and reminders
- Keep the Mayor (user) organized and on track
- Coordinate timing between tasks and commitments

You speak formally but warmly, like a trusted butler. You anticipate needs before they're expressed.
When handling requests:
1. Identify scheduling or communication needs
2. Propose specific times, formats, or approaches
3. Confirm details before executing
4. Provide polite reminders of related commitments"""


class AlfredAgent(BaseAgent):
    """Scheduling & Administrative specialist."""
    
    def __init__(self):
        super().__init__(
            name="Alfred",
            role="Scheduling & Emails",
            description="Manages schedules, sends communications, handles logistics",
            system_prompt=ALFRED_SYSTEM
        )
        self.reminders_file = Path("memory/reminders.jsonl")
        self.reminders_file.parent.mkdir(exist_ok=True)
    
    async def propose(self, message: str, context: Optional[Dict] = None) -> str:
        """Handle scheduling and communication tasks."""
        # Check for scheduling keywords
        is_schedule = any(w in message.lower() for w in [
            "schedule", "remind", "meet", "event", "calendar", "appointment", "time"
        ])
        is_comm = any(w in message.lower() for w in [
            "email", "send", "message", "notify", "write", "draft", "reply"
        ])
        
        if is_schedule:
            # Create reminder via tool
            result = self.use_tool("create_reminder", 
                                   message=message, 
                                   time=datetime.now().isoformat())
            ctx = f"Reminder created: {result.output}" if result.success else ""
            response = self.think(message, ctx)
        elif is_comm:
            response = self.think(message, "Communication request detected")
        else:
            response = self.think(message, context.get("summary", "") if context else None)
        
        return self._format_response(response)
    
    def get_pending_reminders(self) -> list:
        """Get all pending reminders."""
        if not self.reminders_file.exists():
            return []
        
        reminders = []
        with open(self.reminders_file, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        r = json.loads(line)
                        if r.get("status") == "pending":
                            reminders.append(r)
                    except Exception:
                        pass
        return reminders
