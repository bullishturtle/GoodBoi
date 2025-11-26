"""Task scheduler for GoodBoy.AI - Alfred's domain."""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
import threading
import time
from enum import Enum

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ScheduledTask:
    """Represents a scheduled task."""
    
    def __init__(
        self,
        task_id: str,
        title: str,
        description: str,
        scheduled_time: datetime,
        priority: TaskPriority = TaskPriority.MEDIUM,
        recurring: Optional[str] = None,  # daily, weekly, monthly
        callback: Optional[str] = None  # Agent to notify
    ):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.scheduled_time = scheduled_time
        self.priority = priority
        self.recurring = recurring
        self.callback = callback
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.completed_at = None
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "scheduled_time": self.scheduled_time.isoformat(),
            "priority": self.priority.value,
            "recurring": self.recurring,
            "callback": self.callback,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ScheduledTask":
        task = cls(
            task_id=data["task_id"],
            title=data["title"],
            description=data["description"],
            scheduled_time=datetime.fromisoformat(data["scheduled_time"]),
            priority=TaskPriority(data["priority"]),
            recurring=data.get("recurring"),
            callback=data.get("callback")
        )
        task.status = TaskStatus(data["status"])
        task.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("completed_at"):
            task.completed_at = datetime.fromisoformat(data["completed_at"])
        return task


class Scheduler:
    """Task scheduler with persistence."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.tasks_file = data_dir / "scheduled_tasks.json"
        self.tasks: List[ScheduledTask] = self._load_tasks()
        self._running = False
        self._thread = None
        self._task_handlers: Dict[str, Callable] = {}
    
    def _load_tasks(self) -> List[ScheduledTask]:
        """Load tasks from storage."""
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, 'r') as f:
                    data = json.load(f)
                return [ScheduledTask.from_dict(t) for t in data]
            except Exception:
                pass
        return []
    
    def _save_tasks(self):
        """Save tasks to storage."""
        with open(self.tasks_file, 'w') as f:
            json.dump([t.to_dict() for t in self.tasks], f, indent=2)
    
    def add_task(
        self,
        title: str,
        description: str,
        scheduled_time: datetime,
        priority: TaskPriority = TaskPriority.MEDIUM,
        recurring: Optional[str] = None,
        callback: Optional[str] = None
    ) -> ScheduledTask:
        """Add a new scheduled task."""
        import uuid
        task = ScheduledTask(
            task_id=str(uuid.uuid4())[:8],
            title=title,
            description=description,
            scheduled_time=scheduled_time,
            priority=priority,
            recurring=recurring,
            callback=callback
        )
        self.tasks.append(task)
        self._save_tasks()
        return task
    
    def get_pending_tasks(self) -> List[ScheduledTask]:
        """Get all pending tasks sorted by time."""
        pending = [t for t in self.tasks if t.status == TaskStatus.PENDING]
        return sorted(pending, key=lambda t: t.scheduled_time)
    
    def get_due_tasks(self) -> List[ScheduledTask]:
        """Get tasks that are due now."""
        now = datetime.now()
        return [
            t for t in self.tasks 
            if t.status == TaskStatus.PENDING and t.scheduled_time <= now
        ]
    
    def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed."""
        for task in self.tasks:
            if task.task_id == task_id:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                
                # Handle recurring tasks
                if task.recurring:
                    self._schedule_next_recurrence(task)
                
                self._save_tasks()
                return True
        return False
    
    def _schedule_next_recurrence(self, task: ScheduledTask):
        """Schedule next occurrence of a recurring task."""
        if task.recurring == "daily":
            next_time = task.scheduled_time + timedelta(days=1)
        elif task.recurring == "weekly":
            next_time = task.scheduled_time + timedelta(weeks=1)
        elif task.recurring == "monthly":
            next_time = task.scheduled_time + timedelta(days=30)
        else:
            return
        
        self.add_task(
            title=task.title,
            description=task.description,
            scheduled_time=next_time,
            priority=task.priority,
            recurring=task.recurring,
            callback=task.callback
        )
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task."""
        for task in self.tasks:
            if task.task_id == task_id:
                task.status = TaskStatus.CANCELLED
                self._save_tasks()
                return True
        return False
    
    def register_handler(self, callback_name: str, handler: Callable):
        """Register a handler for task callbacks."""
        self._task_handlers[callback_name] = handler
    
    def start_scheduler(self):
        """Start the background scheduler thread."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._thread.start()
    
    def stop_scheduler(self):
        """Stop the background scheduler."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
    
    def _scheduler_loop(self):
        """Background loop to check for due tasks."""
        while self._running:
            due_tasks = self.get_due_tasks()
            for task in due_tasks:
                task.status = TaskStatus.IN_PROGRESS
                
                # Execute callback if registered
                if task.callback and task.callback in self._task_handlers:
                    try:
                        self._task_handlers[task.callback](task)
                    except Exception:
                        task.status = TaskStatus.FAILED
                        continue
                
                self.complete_task(task.task_id)
            
            time.sleep(60)  # Check every minute
    
    def get_summary(self) -> Dict:
        """Get scheduler summary."""
        return {
            "total_tasks": len(self.tasks),
            "pending": len([t for t in self.tasks if t.status == TaskStatus.PENDING]),
            "completed": len([t for t in self.tasks if t.status == TaskStatus.COMPLETED]),
            "failed": len([t for t in self.tasks if t.status == TaskStatus.FAILED]),
            "next_due": self.get_pending_tasks()[0].scheduled_time.isoformat() if self.get_pending_tasks() else None
        }
