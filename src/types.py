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
    ACTIVE = "active"
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    WORKING = "working"
    LEARNING = "learning"

class InteractionType(Enum):
    COLLABORATION = "collaboration"
    HELP_REQUEST = "help_request"
    HELP_OFFER = "help_offer"
    KNOWLEDGE_SHARE = "knowledge_share"
    FEEDBACK = "feedback"

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

@dataclass
class SubTask:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    status: TaskStatus = TaskStatus.BACKLOG
    assigned_to: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    required_knowledge: List[str] = field(default_factory=list)
    progress: float = 0.0

    def can_start(self, completed_subtasks: List[str]) -> bool:
        return all(dep_id in completed_subtasks for dep_id in self.dependencies)
    
@dataclass
class InteractionRecord:
    """Records details of an interaction between agents."""
    timestamp: int
    initiator_id: str
    recipient_id: str
    interaction_type: InteractionType
    duration: float
    knowledge_shared: List[str] = field(default_factory=list)