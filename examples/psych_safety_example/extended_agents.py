"""Extended agent with psychological safety attributes."""

import random
from src.engineering.agents import EngineerAgent

class PsychSafetyEngineerAgent(EngineerAgent):
    """Engineer agent extended with psychological safety and team efficacy attributes."""
    
    def __init__(self, unique_id: int, model):
        super().__init__(unique_id, model)
        
        # Add psychological safety attributes
        self.perceived_psychological_safety = random.uniform(0.0, 1.0)
        self.contributed_psychological_safety = random.uniform(-1.0, 1.0)
        self.perceived_team_efficacy = 0.5
