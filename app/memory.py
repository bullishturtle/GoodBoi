import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class MemoryManager:
    """Manages conversation memory and semantic storage."""
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.messages_file = memory_dir / "messages.jsonl"
        self.messages = self._load_messages()
    
    def _load_messages(self) -> List[Dict]:
        """Load messages from storage."""
        messages = []
        if self.messages_file.exists():
            with open(self.messages_file, 'r') as f:
                for line in f:
                    if line.strip():
                        messages.append(json.loads(line))
        return messages
    
    def add_message(self, user_message: Optional[str] = None, assistant_message: Optional[str] = None):
        """Add message to memory."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "assistant": assistant_message
        }
        self.messages.append(entry)
        
        # Persist
        with open(self.messages_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def get_context(self, k: int = 10) -> Dict:
        """Get recent context for agent decision-making."""
        recent = self.messages[-k:] if len(self.messages) > k else self.messages
        return {
            "recent_messages": recent,
            "conversation_length": len(self.messages),
            "last_interaction": self.messages[-1]["timestamp"] if self.messages else None
        }
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search memories (simple keyword matching)."""
        results = []
        query_lower = query.lower()
        
        for msg in self.messages[::-1]:  # Search backwards (recent first)
            if msg.get("user") and query_lower in msg["user"].lower():
                results.append({
                    "timestamp": msg["timestamp"],
                    "text": msg["user"],
                    "type": "user_message"
                })
            if len(results) >= k:
                break
        
        return results
    
    def cleanup_old_entries(self, days: int = 30):
        """Remove messages older than specified days."""
        cutoff = datetime.now() - timedelta(days=days)
        self.messages = [
            m for m in self.messages
            if datetime.fromisoformat(m["timestamp"]) > cutoff
        ]
        
        # Re-write file
        with open(self.messages_file, 'w') as f:
            for m in self.messages:
                f.write(json.dumps(m) + '\n')
