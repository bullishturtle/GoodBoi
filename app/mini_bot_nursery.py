import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import uuid

class MiniBotNursery:
    """Generates and manages mini-bots (specialized sub-agents that evolve)."""
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.minibots_file = memory_dir / "minibots.jsonl"
        self.minibots = self._load_minibots()
    
    def _load_minibots(self) -> List[Dict]:
        """Load existing mini-bots."""
        minibots = []
        if self.minibots_file.exists():
            with open(self.minibots_file, 'r') as f:
                for line in f:
                    if line.strip():
                        minibots.append(json.loads(line))
        return minibots
    
    def spawn_minibot(self, 
                     specialization: str,
                     parent_agent: str,
                     trigger_pattern: str) -> Dict:
        """Create new mini-bot for specialized task handling."""
        
        minibot = {
            "id": str(uuid.uuid4())[:8],
            "name": f"{parent_agent}_mini_{len(self.minibots)}",
            "specialization": specialization,
            "parent_agent": parent_agent,
            "trigger_pattern": trigger_pattern,
            "created_at": datetime.now().isoformat(),
            "performance": 1.0,
            "interactions": 0,
            "status": "active"
        }
        
        self.minibots.append(minibot)
        
        # Persist
        with open(self.minibots_file, 'a') as f:
            f.write(json.dumps(minibot) + '\n')
        
        return minibot
    
    def update_minibot_performance(self, minibot_id: str, quality: float):
        """Update mini-bot's performance metrics."""
        for bot in self.minibots:
            if bot["id"] == minibot_id:
                bot["interactions"] += 1
                bot["performance"] = (bot["performance"] * (bot["interactions"] - 1) + quality) / bot["interactions"]
                
                # Retire low performers
                if bot["performance"] < 0.3:
                    bot["status"] = "retired"
                
                break
        
        # Persist
        with open(self.minibots_file, 'w') as f:
            for bot in self.minibots:
                f.write(json.dumps(bot) + '\n')
    
    def get_active_minibots(self) -> List[Dict]:
        """Get all active mini-bots."""
        return [bot for bot in self.minibots if bot["status"] == "active"]
