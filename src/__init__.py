# Main package initialization

from .model import EngineeringTeamModel
from .agents import BaseAgent, EngineerAgent, ManagerAgent
from .agents.components.task_tracker import TaskStatus, Task

__all__ = [
    'EngineeringTeamModel',
    'BaseAgent', 
    'EngineerAgent', 
    'ManagerAgent',
    'TaskStatus',
    'Task'
]