import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict

class LearningEngine:
    """Self-learning engine that discovers patterns and optimizes routing."""
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.patterns_file = memory_dir / "learned_patterns.jsonl"
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> List[Dict]:
        """Load learned patterns."""
        patterns = []
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r') as f:
                for line in f:
                    if line.strip():
                        patterns.append(json.loads(line))
        return patterns
    
    def learn_from_interaction(self, 
                               message: str, 
                               agents_used: List[str],
                               output_quality: float):
        """Learn from successful interactions."""
        
        # Extract keywords
        keywords = self._extract_keywords(message)
        
        pattern = {
            "timestamp": datetime.now().isoformat(),
            "keywords": keywords,
            "agents": agents_used,
            "quality": output_quality,
            "message_length": len(message)
        }
        
        self.patterns.append(pattern)
        
        # Persist
        with open(self.patterns_file, 'a') as f:
            f.write(json.dumps(pattern) + '\n')
    
    def _extract_keywords(self, message: str, top_k: int = 5) -> List[str]:
        """Extract key terms from message."""
        words = message.lower().split()
        # Filter common words
        stopwords = {"the", "a", "an", "and", "or", "is", "are", "to", "for"}
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        return keywords[:top_k]
    
    def suggest_routing_optimization(self) -> Optional[Dict]:
        """Suggest routing optimizations based on learned patterns."""
        if len(self.patterns) < 10:
            return None
        
        # Find most successful agent combinations
        agent_combos = defaultdict(list)
        for pattern in self.patterns[-100:]:  # Recent patterns
            key = tuple(sorted(pattern["agents"]))
            agent_combos[key].append(pattern["quality"])
        
        best_combo = max(
            agent_combos.items(),
            key=lambda x: sum(x[1]) / len(x[1])
        )
        
        return {
            "suggested_agents": list(best_combo[0]),
            "avg_quality": sum(best_combo[1]) / len(best_combo[1]),
            "frequency": len(best_combo[1]),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_routing_hint(self, keywords: List[str]) -> Optional[List[str]]:
        """Get suggested agents based on keywords."""
        matching_patterns = []
        
        for pattern in self.patterns[::-1]:  # Search backwards
            if any(kw in pattern.get("keywords", []) for kw in keywords):
                matching_patterns.append(pattern)
            
            if len(matching_patterns) >= 5:
                break
        
        if not matching_patterns:
            return None
        
        # Most common agents in matching patterns
        agent_scores = defaultdict(int)
        for pattern in matching_patterns:
            for agent in pattern["agents"]:
                agent_scores[agent] += 1
        
        return [agent for agent, _ in sorted(agent_scores.items(), 
                                             key=lambda x: x[1], 
                                             reverse=True)][:2]
