"""
Task system for engineering simulation.
"""

import uuid
import random
from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from ..framework.interfaces import TaskGenerator

class TaskStatus(Enum):
    BACKLOG = "backlog"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

class SubTaskStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ACTIVE = "active"
    WORKING = "working"
    LEARNING = "learning"

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
    start_step: int = 0
    stop_step: int = 0

    def is_complete(self) -> bool:
        return self.status == SubTaskStatus.COMPLETED
    
    def start(self, step: int = None):
        if self.status == SubTaskStatus.NOT_STARTED:
            if step:
                self.start_step = step
            self.status = SubTaskStatus.IN_PROGRESS
        else:
            raise ValueError(f"Cannot start subtask with status {self.status}")

    def complete(self, step: int = None):
        if step:
            self.stop_step = step
        self.status = SubTaskStatus.COMPLETED
        self.progress = 1.0

    def pause(self):
        if self.status == SubTaskStatus.IN_PROGRESS:
            self.status = SubTaskStatus.NOT_STARTED
        else:
            raise ValueError(f"Cannot pause subtask with status {self.status}")

@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    status: TaskStatus = TaskStatus.BACKLOG
    assigned_to: Optional[str] = None
    difficulty: int = field(default_factory=lambda: random.randint(1, 10))
    subtasks: List[SubTask] = field(default_factory=list)
    start_step: int = 0
    stop_step: int = 0

    def get_progress(self) -> float:
        if not self.subtasks:
            return 0.0
        completed_subtasks = len([task for task in self.subtasks if task.is_complete()])
        return completed_subtasks / len(self.subtasks)

    def start(self, step: int = None):
        if self.status == TaskStatus.BACKLOG:
            if step:
                self.start_step = step
            self.status = TaskStatus.IN_PROGRESS
        else:
            raise ValueError(f"Cannot start task with status {self.status}")

    def complete(self, step: int = None):
        if self.status == TaskStatus.IN_PROGRESS:
            if step:
                self.stop_step = step
            self.status = TaskStatus.COMPLETED
        else:
            raise ValueError(f"Cannot complete task with status {self.status}")

    def pause(self):
        if self.status == TaskStatus.IN_PROGRESS:
            self.status = TaskStatus.BACKLOG
        else:
            raise ValueError(f"Cannot pause task with status {self.status}")

    def assign(self, assignee: str):
        self.assigned_to = assignee

    def unassign(self):
        self.assigned_to = None

class EngineeringTaskGenerator(TaskGenerator):
    """Generates engineering tasks for the simulation."""
    
    def __init__(self, task_creation_rate: float = 0.1, max_tasks: int = 50):
        self.task_creation_rate = task_creation_rate
        self.max_tasks = max_tasks
        self.tasks_created = 0
    
    def should_generate(self, model) -> bool:
        """Determine if a new task should be generated."""
        if not hasattr(model, 'tasks') or self.tasks_created >= self.max_tasks:
            return False
        
        return random.random() < self.task_creation_rate
    
    def generate_task(self, model, context: Dict[str, Any] = None) -> Task:
        """Generate a new engineering task."""
        self.tasks_created += 1
        difficulty = random.randint(1, 10)
        
        task = Task(
            name=f"Engineering Task {self.tasks_created}",
            difficulty=difficulty
        )
        
        # Create subtasks
        num_subtasks = difficulty
        for i in range(num_subtasks):
            required_knowledge = []
            if hasattr(model, 'knowledge_space'):
                required_knowledge = random.sample(
                    model.knowledge_space,
                    k=min(random.randint(1, 5), len(model.knowledge_space))
                )
            
            subtask = SubTask(
                name=f"{task.name} - Subtask {i+1}",
                required_knowledge=required_knowledge,
                difficulty=random.randint(1, 5)
            )
            task.subtasks.append(subtask)
        
        # Add task to model if it has a task storage
        if hasattr(model, 'tasks'):
            model.tasks[task.id] = task
        
        return task