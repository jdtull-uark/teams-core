import mesa
from typing import Any, Dict
from ..model import EngineeringTeamModel

class BaseAgent(mesa.Agent):
    """Base class for all agents in the engineering team model."""
    
    def __init__(self, unique_id: int, model: 'EngineeringTeamModel'):
        super().__init__(unique_id, model)
        # TODO: Add attributes
        
    def step(self):
        """Standard Mesa step function."""
        # TODO: Add behavior rules
        pass