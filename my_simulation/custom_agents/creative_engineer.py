from src.framework.core.agent import BaseAgent
from src.engineering.agents import EngineerAgent
import random

class CreativeEngineerAgent(EngineerAgent):
    '''An engineer with enhanced creativity and innovation capabilities.'''
    
    def __init__(self, unique_id: int, model):
        super().__init__(unique_id, model)
        self.creativity_level = random.uniform(0.5, 1.0)
        self.innovation_bonus = 0.2
        
        # Boost work efficiency based on creativity
        self.work_efficiency *= (1 + self.creativity_level * self.innovation_bonus)
    
    def step(self):
        super().step()
        
        # Creative agents occasionally have breakthrough moments
        if random.random() < 0.01 * self.creativity_level:
            self.log_action("creative_breakthrough", {
                "creativity_level": self.creativity_level
            })
            # Boost motivation temporarily
            self.motivation = min(1.0, self.motivation + 0.1)