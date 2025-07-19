from .base import BaseAgent
from .engineer import EngineerAgent
from typing import TYPE_CHECKING # NEW: Import TYPE_CHECKING

if TYPE_CHECKING:
    from ..model import EngineeringTeamModel

class ManagerAgent(BaseAgent):
    """Represents a team manager who assigns tasks."""
    
    def __init__(self, unique_id: int, model: 'EngineeringTeamModel'):
        super().__init__(unique_id, model)
        # TODO: Add management_attributes
        
    def assign_tasks(self):
        """Assign available tasks to engineers."""
        available_tasks = [t for t in self.model.tasks.values() 
                          if t.status == TaskStatus.BACKLOG]
        available_engineers = [a for a in self.model.agents 
                             if isinstance(a, EngineerAgent) and a.current_task is None]
        
        # Simple assignment: first available task to first available engineer
        if available_tasks and available_engineers:
            task = available_tasks[0]
            engineer = available_engineers[0]
            
            task.assigned_to = engineer.unique_id
            task.status = TaskStatus.IN_PROGRESS
            engineer.current_task = task
    
    def step(self):
        """Manager step behavior."""
        self.assign_tasks()
        # TODO: Add manager rules