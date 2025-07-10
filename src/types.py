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

class InteractionType(Enum):
    COLLABORATION = "collaboration"
    HELP_REQUEST = "help_request"
    HELP_OFFER = "help_offer"
    KNOWLEDGE_SHARE = "knowledge_share"
    DISCUSSION = "discussion"
    FEEDBACK = "feedback"

@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    status: TaskStatus = TaskStatus.BACKLOG
    assigned_to: Optional[str] = None
    difficulty: int = field(default_factory=lambda: random.randint(1, 10))
    remaining_work: int = field(default_factory=lambda: 0)
    dependencies: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.remaining_work == 0:
            self.remaining_work = self.difficulty * 10