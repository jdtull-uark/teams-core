# Main package initialization

from .model import EngineeringTeamModel
from .agents import BaseAgent, EngineerAgent, ManagerAgent

__all__ = [
    'EngineeringTeamModel',
    'BaseAgent', 
    'EngineerAgent', 
    'ManagerAgent',
    'TaskStatus',
    'Task'
]