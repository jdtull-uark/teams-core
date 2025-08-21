"""
Task system for engineering simulation.
"""

import uuid
import random
from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from ..framework.core.interfaces import TaskGenerator

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
    difficulty: int = field(default_factory=lambda: random.randint(1, 10))
    required_steps: int = field(init=True, default=0)  # Will be set based on difficulty
    steps_completed: int = 0
    progress: float = 0.0
    start_step: int = 0
    stop_step: int = 0

    def __post_init__(self):
        if self.required_steps == 0:
            self.required_steps = self.difficulty * 2  # Base steps on difficulty

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
        # print(f"Subtask {self.name} completed after {self.steps_completed} steps (required: {self.required_steps})")

    def pause(self):
        if self.status == SubTaskStatus.IN_PROGRESS:
            self.status = SubTaskStatus.NOT_STARTED
        else:
            raise ValueError(f"Cannot pause subtask with status {self.status}")
        
    def grade(self, current_step: int = None) -> float:
        """
        Calculate a grade based on efficiency.
        1.0 = completed in exactly required steps
        > 1.0 = completed faster than required (exceptional performance)
        < 1.0 = took more steps than required (less efficient)
        Theoretical max is around 2.0 for tasks completed in half the required time
        """
        if self.status == SubTaskStatus.COMPLETED:
            # Calculate actual steps taken
            actual_steps = self.stop_step - self.start_step
            if actual_steps <= 0:
                return 2.0  # Edge case: instant completion gets max reward
            
            required_steps_with_learning = self.required_steps + len(self.required_knowledge) / 0.3 # 0.3 is the average learning rate in agent init

            # Grade based on efficiency: required_steps / actual_steps
            # This allows grades > 1.0 for exceptional performance
            grade = required_steps_with_learning / actual_steps
            return max(0.0, grade)
            
        elif self.status == SubTaskStatus.IN_PROGRESS:
            if current_step is None:
                # print("Cannot grade an in-progress subtask without current step!")
                return 0.0
            
            # For in-progress tasks, estimate based on current progress
            actual_steps_so_far = current_step - self.start_step
            if actual_steps_so_far <= 0:
                return 1.0  # Just started, assume average performance
            
            # Estimate what the final grade would be if we maintain current pace
            estimated_total_steps = actual_steps_so_far / self.progress if self.progress > 0 else actual_steps_so_far * 2
            estimated_grade = self.required_steps / estimated_total_steps
            return max(0.0, estimated_grade)
        
        else:
            # Not started or other status
            return 0.0
            
            

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
            # print(f"Task {self.name} completed with {len([st for st in self.subtasks if st.is_complete()])} completed subtasks out of {len(self.subtasks)}")
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
    
    def grade(self, current_step: int = None) -> float:
        """
        Calculate overall task grade based on average subtask grades.
        Returns grade where 1.0 = average efficiency, >1.0 = exceptional performance.
        """
        if not self.subtasks:
            return 0.0
        
        total_grade = 0.0
        graded_subtasks = 0
        
        for subtask in self.subtasks:
            subtask_grade = subtask.grade(current_step)
            if subtask_grade > 0 or subtask.status == SubTaskStatus.COMPLETED:
                total_grade += subtask_grade
                graded_subtasks += 1
        
        if graded_subtasks == 0:
            return 0.0
        
        return total_grade / graded_subtasks

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
        
        return model.random.random() < self.task_creation_rate
    
    def generate_task(self, model, context: Dict[str, Any] = None) -> Task:
        """Generate a new engineering task."""
        self.tasks_created += 1
        difficulty = model.random.randint(1, 10)
        
        task = Task(
            name=f"Engineering Task {self.tasks_created}",
            difficulty=difficulty
        )
        
        # Create subtasks
        num_subtasks = difficulty
        for i in range(num_subtasks):
            required_knowledge = []
            if hasattr(model, 'knowledge_space'):
                required_knowledge = model.random.sample(
                    model.knowledge_space,
                    k=min(model.random.randint(1, 5), len(model.knowledge_space))
                )
            
            subtask = SubTask(
                name=f"{task.name} - Subtask {i+1}",
                required_knowledge=required_knowledge,
                difficulty=model.random.randint(1, 5)
            )
            task.subtasks.append(subtask)
        
        # Add task to model if it has a task storage
        if hasattr(model, 'tasks'):
            model.tasks[task.id] = task
        
        return task