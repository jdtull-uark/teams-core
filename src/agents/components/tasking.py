from typing import List, Optional, TYPE_CHECKING
from enum import StrEnum
from dataclasses import dataclass, field
import uuid
import random

if TYPE_CHECKING:
    from ..engineer import EngineerAgent

class TaskStatus(StrEnum):
    BACKLOG = "backlog"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

class SubTaskStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    status: TaskStatus = TaskStatus.BACKLOG
    assigned_to: Optional[str] = None
    difficulty: int = field(default_factory=lambda: random.randint(1, 10))
    subtasks: List['SubTask'] = field(default_factory=list)
    start_time: Optional[int] = None  # Step when task was started

    def get_progress(self) -> float:
        """Calculate task progress based on completed subtasks."""
        if not self.subtasks:
            return 0.0
        completed_subtasks = sum(1 for task in self.subtasks if task.status == SubTaskStatus.COMPLETED)
        return completed_subtasks / len(self.subtasks)

    def start(self, step: int = 0):
        """Start the task by changing status to IN_PROGRESS"""
        if self.status == TaskStatus.BACKLOG:
            self.status = TaskStatus.IN_PROGRESS
            self.start_time = step
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
    required_steps: int = field(default_factory=lambda: random.randint(1, 10))
    difficulty: int = field(default_factory=lambda: random.randint(1, 10))
    steps_completed: int = 0
    progress: float = 0.0
    start_time: Optional[int] = None  # Step when subtask was started

    def is_complete(self) -> bool:
        """Check if the subtask is completed"""
        return self.status == SubTaskStatus.COMPLETED

    def can_start(self, completed_subtasks: List[str]) -> bool:
        """Check if all dependencies are satisfied"""
        if not completed_subtasks:
            completed_subtasks = []
        return all(dep_id in completed_subtasks for dep_id in self.dependencies)
    
    def start(self, completed_subtasks: List[str] = None, step: int = 0):
        """Start the subtask"""
        if completed_subtasks is None:
            completed_subtasks = []
            
        if not self.can_start(completed_subtasks):
            raise ValueError("Cannot start: dependencies not met")
        
        if self.status == SubTaskStatus.NOT_STARTED:
            self.status = SubTaskStatus.IN_PROGRESS
            self.start_time = step
        else:
            raise ValueError(f"Cannot start subtask with status {self.status}")

    def complete(self):
        """Mark the subtask as completed"""
        if self.status == SubTaskStatus.IN_PROGRESS:
            self.status = SubTaskStatus.COMPLETED
            self.progress = 1.0
        else:
            raise ValueError(f"Cannot complete subtask with status {self.status}")

    def pause(self):
        """Pause the subtask"""
        if self.status == SubTaskStatus.IN_PROGRESS:
            self.status = SubTaskStatus.NOT_STARTED
        else:
            raise ValueError(f"Cannot pause subtask with status {self.status}")

class Tasking:
    """Handles all task and subtask management for an engineer agent."""
    
    def __init__(self, agent: 'EngineerAgent'):
        self.agent = agent
        self.assigned_tasks: List[Task] = []
        self.current_task: Optional[Task] = None
        self.current_subtask: Optional[SubTask] = None
        self.completed_tasks: List[str] = []
        self.completed_subtasks: List[str] = []
        self.all_tasks_completed: bool = False
    
    def get_next_available_task(self) -> Optional[Task]:
        """Get the next available task from the backlog."""
        return next(
            (task for task in self.assigned_tasks if task.status == TaskStatus.BACKLOG), 
            None
        )
    
    def start_next_task(self) -> bool:
        """Start the next available task. Returns True if a task was started."""
        if self.current_task:
            return False
        
        next_task = self.get_next_available_task()
        if next_task:
            self.current_task = next_task
            self.current_task.start(self.agent.model.steps)
            self.agent._log_history("task_started", {"task_id": self.current_task.id})
            return True
        
        return False
    
    def get_next_subtask(self) -> Optional[SubTask]:
        """Get the next subtask to work on."""
        if not self.current_task:
            return None
        
        # Try to find an in-progress subtask
        active_subtask = next(
            (subtask for subtask in self.current_task.subtasks 
             if subtask.status == SubTaskStatus.IN_PROGRESS), 
            None
        )
        
        if active_subtask:
            return active_subtask
        
        # If no active subtask, start the first available unstarted subtask
        for subtask in self.current_task.subtasks:
            if (subtask.status == SubTaskStatus.NOT_STARTED and 
                subtask.can_start(self.completed_subtasks)):
                try:
                    subtask.start(self.completed_subtasks, step=self.agent.model.steps)
                    return subtask
                except ValueError:
                    continue
        
        return None
    
    def work_on_current_subtask(self):
        """Progress work on the current subtask."""
        if not self.current_subtask:
            return
        
        self.agent._log_history("work_on_subtask", {
            "subtask_id": self.current_subtask.id,
            "progress": self.current_subtask.progress
        })
        
        if self.agent.knowledge_manager.has_all_required_knowledge():
            # If all required knowledge is known, work on the subtask
            progress_increment = self.agent.work_efficiency * 0.1
            self.current_subtask.progress += progress_increment
            
            if self.current_subtask.progress >= 1.0:
                self.complete_current_subtask()
        else:
            # Learn missing knowledge
            self.attempt_learning()
    
    def complete_current_subtask(self):
        """Complete the current subtask and clean up."""
        if not self.current_subtask:
            return
        
        try:
            self.current_subtask.complete()
            self.completed_subtasks.append(self.current_subtask.id)
            self.agent._log_history("subtask_completed", {
                "subtask_id": self.current_subtask.id
            })
            
            # Reset seeking behavior
            self.agent.seeking_knowledge = False
            self.agent.searching_agents = False
            self.agent.searching_agents_targets = []
            
            # Move to next subtask or complete task
            self.current_subtask = None
            self.check_task_completion()
        except ValueError as e:
            self.agent._log_history("subtask_completion_failed", {
                "subtask_id": self.current_subtask.id,
                "error": str(e)
            })
    
    def check_task_completion(self):
        """Check if current task is completed and handle completion."""
        if not self.current_task:
            return
        
        if all(subtask.status == SubTaskStatus.COMPLETED for subtask in self.current_task.subtasks):
            # All subtasks completed, mark task as completed
            try:
                self.current_task.complete()
                self.completed_tasks.append(self.current_task.id)
                self.agent._log_history("task_completed", {"task_id": self.current_task.id})
                self.current_task = None
                
                # Check if all tasks are completed
                if all(task.status == TaskStatus.COMPLETED for task in self.assigned_tasks):
                    self.all_tasks_completed = True
                    self.agent._log_history("all_tasks_completed", {
                        "engineer_id": self.agent.unique_id
                    })
            except ValueError as e:
                self.agent._log_history("task_completion_failed", {
                    "task_id": self.current_task.id,
                    "error": str(e)
                })
    
    def attempt_learning(self):
        """Attempt to learn missing knowledge for current subtask."""
        if not self.current_subtask:
            return
        
        missing_knowledge = self.agent.knowledge_manager.get_missing_knowledge(self.current_subtask.required_knowledge)
        if not missing_knowledge:
            return
        
        self.agent.seeking_knowledge = True
        
        # Try to learn each missing concept
        for concept in missing_knowledge:
            if self.agent.knowledge_manager.knows_agent_with_knowledge(concept):
                self.agent.searching_agents = True
                self.agent.searching_agents_targets = (
                    self.agent.knowledge_manager.find_agents_with_needed_knowledge()
                )
            
            self.agent.knowledge_manager.learn_concept(concept)
    
    def work_on_task(self):
        """Main work method - coordinates task and subtask work."""
        # Start a new task if needed
        if not self.current_task:
            if not self.start_next_task():
                return
        
        if self.current_task and self.current_task.status == TaskStatus.IN_PROGRESS:
            if not self.current_subtask:
                self.current_subtask = self.get_next_subtask()
            
            if self.current_subtask:
                self.work_on_current_subtask()
    
    def assign_task(self, task: Task):
        """Assign a new task to this agent."""
        task.assign(self.agent.unique_id)
        self.assigned_tasks.append(task)
    
    def get_progress_summary(self) -> dict:
        """Get a summary of task progress."""
        return {
            "total_tasks": len(self.assigned_tasks),
            "completed_tasks": len(self.completed_tasks),
            "current_task_id": self.current_task.id if self.current_task else None,
            "current_subtask_id": self.current_subtask.id if self.current_subtask else None,
            "all_completed": self.all_tasks_completed,
            "current_task_progress": self.current_task.get_progress() if self.current_task else 0.0
        }