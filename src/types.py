# Core data types and enums for the engineering team model

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import uuid
import random

# =============================================================================
# ENUMS AND DATA CLASSES
# =============================================================================

class TaskStatus(Enum):
    BACKLOG = "backlog"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

class SubTaskStatus(Enum):
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    WORKING = "working"
    LEARNING = "learning"


@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    status: TaskStatus = TaskStatus.BACKLOG
    assigned_to: Optional[str] = None
    difficulty: int = field(default_factory=lambda: random.randint(1, 10))
    subtasks: List['SubTask'] = field(default_factory=list)

    def get_progress(self) -> float:
        completed_subtasks = len([task for task in self.subtasks if task.status == "completed"])
        return completed_subtasks / self.difficulty

    def start(self):
        """Start the task by changing status to IN_PROGRESS"""
        if self.status == TaskStatus.BACKLOG:
            self.status = TaskStatus.IN_PROGRESS
        else:
            raise ValueError(f"Cannot start task with status {self.status}")

    def complete(self):
        """Complete the task by changing status to COMPLETED"""
        if self.status == TaskStatus.IN_PROGRESS:
            self.status = TaskStatus.COMPLETED
        else:
            raise ValueError(f"Cannot complete task with status {self.status}")

    def pause(self):
        """Pause an in-progress task"""
        if self.status == TaskStatus.IN_PROGRESS:
            self.status = TaskStatus.BACKLOG
        else:
            raise ValueError(f"Cannot pause task with status {self.status}")

    def assign(self, assignee: str):
        """Assign the task to someone"""
        self.assigned_to = assignee

    def unassign(self):
        """Remove task assignment"""
        self.assigned_to = None

@dataclass
class SubTask:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    status: SubTaskStatus = SubTaskStatus.NOT_STARTED
    assigned_to: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    required_knowledge: List[str] = field(default_factory=list)
    required_steps: int = 0
    difficulty: int = field(default_factory=lambda: random.randint(1, 10))
    steps_completed: int = 0
    progress: float = 0.0

    def is_complete(self) -> bool:
        """Check if the subtask is completed"""
        return self.status == SubTaskStatus.COMPLETED

    def can_start(self, completed_subtasks: List[str]) -> bool:
        return all(dep_id in completed_subtasks for dep_id in self.dependencies)
    
    def start(self, completed_subtasks: List[str] = None):
        """Start the subtask"""
        
        if not self.can_start(completed_subtasks):
            raise ValueError("Cannot start: dependencies not met")
        
        if self.status == SubTaskStatus.NOT_STARTED:
            self.status = SubTaskStatus.IN_PROGRESS
        else:
            raise ValueError(f"Cannot start subtask with status {self.status}")

    def complete(self):
        """Mark the subtask as completed"""
        self.status = SubTaskStatus.COMPLETED

    def pause(self):
        """Pause the subtask"""
        if self.status == SubTaskStatus.IN_PROGRESS:
            self.status = SubTaskStatus.NOT_STARTED
        else:
            raise ValueError(f"Cannot pause subtask with status {self.status}")
