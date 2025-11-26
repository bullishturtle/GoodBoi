"""Teachings Store - Persistent knowledge base that learns from interactions."""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict, field


@dataclass
class Lesson:
    """A single teaching/lesson stored in memory."""
    id: str
    topic: str
    instruction: str
    tags: List[str]
    created_at: str
    usage_count: int = 0
    effectiveness_score: float = 0.5
    source: str = "user"  # user, reflection, correction


class TeachingsStore:
    """Persistent store for lessons and corrections that improve over time."""
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.file_path = memory_dir / "teachings.jsonl"
        self.lessons: List[Lesson] = []
        self._load()
    
    def _load(self):
        """Load lessons from disk."""
        if not self.file_path.exists():
            return
        
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        self.lessons.append(Lesson(**data))
                    except Exception:
                        pass
    
    def _save(self):
        """Persist all lessons to disk."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            for lesson in self.lessons:
                f.write(json.dumps(asdict(lesson)) + "\n")
    
    def add_lesson(
        self,
        topic: str,
        instruction: str,
        tags: Optional[List[str]] = None,
        source: str = "user"
    ) -> Lesson:
        """Add a new lesson to the store."""
        lesson = Lesson(
            id=f"lesson_{len(self.lessons)}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            topic=topic,
            instruction=instruction,
            tags=tags or [],
            created_at=datetime.now().isoformat(),
            source=source
        )
        self.lessons.append(lesson)
        self._save()
        return lesson
    
    def get_relevant_lessons(self, query: str, k: int = 5) -> List[Lesson]:
        """Find lessons relevant to query."""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored = []
        for lesson in self.lessons:
            score = 0
            # Topic match
            if query_lower in lesson.topic.lower():
                score += 3
            # Tag match
            for tag in lesson.tags:
                if tag.lower() in query_words:
                    score += 2
            # Instruction keyword match
            instruction_words = set(lesson.instruction.lower().split())
            overlap = len(query_words & instruction_words)
            score += overlap
            # Boost by effectiveness
            score *= (0.5 + lesson.effectiveness_score)
            
            if score > 0:
                scored.append((score, lesson))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [lesson for _, lesson in scored[:k]]
    
    def mark_lesson_used(self, lesson_id: str, was_helpful: bool = True):
        """Track lesson usage and effectiveness."""
        for lesson in self.lessons:
            if lesson.id == lesson_id:
                lesson.usage_count += 1
                # Adjust effectiveness based on feedback
                delta = 0.1 if was_helpful else -0.1
                lesson.effectiveness_score = max(0, min(1, lesson.effectiveness_score + delta))
                self._save()
                break
    
    def get_all_by_topic(self, topic: str) -> List[Lesson]:
        """Get all lessons for a topic."""
        return [l for l in self.lessons if l.topic.lower() == topic.lower()]


# Global singleton
_store: Optional[TeachingsStore] = None


def get_store(memory_dir: Optional[Path] = None) -> TeachingsStore:
    """Get or create the teachings store singleton."""
    global _store
    if _store is None:
        path = memory_dir or Path("memory")
        path.mkdir(exist_ok=True)
        _store = TeachingsStore(path)
    return _store
