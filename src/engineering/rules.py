"""
Engineering-specific rules for the simulation.
"""

import random
from typing import TYPE_CHECKING
from ..framework.interfaces import Rule

if TYPE_CHECKING:
    from ..framework.core.model import BaseModel

class PsychologicalSafetyRule(Rule):
    """Rule that manages psychological safety in the team."""
    
    def __init__(self, base_change_rate: float = 0.01, threshold: float = 0.7):
        self.base_change_rate = base_change_rate
        self.threshold = threshold
    
    def should_apply(self, model: 'BaseModel') -> bool:
        """Apply this rule every step."""
        return True
    
    def apply(self, model: 'BaseModel') -> None:
        """Apply psychological safety updates to the model and agents."""
        # Update model-level psychological safety
        if not hasattr(model, 'psychological_safety'):
            model.psychological_safety = 0.5
        
        # Collect agent psychological safety contributions
        total_cps = 0
        agent_count = 0
        
        for agent in model.agents:
            if hasattr(agent, 'contributed_psychological_safety'):
                total_cps += agent.contributed_psychological_safety
                agent_count += 1
        
        if agent_count > 0:
            # Update model psychological safety based on agent contributions
            avg_contribution = total_cps / agent_count
            model.psychological_safety += avg_contribution * self.base_change_rate
            model.psychological_safety = max(0.0, min(1.0, model.psychological_safety))
        
        # Update individual agent perceived psychological safety
        for agent in model.agents:
            if hasattr(agent, 'perceived_psychological_safety'):
                # Agent's perception moves toward model's actual psychological safety
                difference = model.psychological_safety - agent.perceived_psychological_safety
                change = difference * self.base_change_rate * random.uniform(0.5, 1.5)
                agent.perceived_psychological_safety += change
                agent.perceived_psychological_safety = max(0.0, min(1.0, agent.perceived_psychological_safety))
                
                # Psychological safety affects motivation and communication
                if hasattr(agent, 'motivation'):
                    if agent.perceived_psychological_safety > self.threshold:
                        agent.motivation = min(1.0, agent.motivation + 0.01)
                    else:
                        agent.motivation = max(0.1, agent.motivation - 0.01)

class ProductivityRule(Rule):
    """Rule that affects productivity based on various factors."""
    
    def should_apply(self, model: 'BaseModel') -> bool:
        """Apply every 10 steps."""
        return model.step_count % 10 == 0
    
    def apply(self, model: 'BaseModel') -> None:
        """Adjust agent productivity based on psychological safety and other factors."""
        for agent in model.agents:
            if hasattr(agent, 'work_efficiency') and hasattr(agent, 'perceived_psychological_safety'):
                # Higher psychological safety improves efficiency
                if agent.perceived_psychological_safety > 0.7:
                    agent.work_efficiency = min(2.0, agent.work_efficiency + 0.05)
                elif agent.perceived_psychological_safety < 0.3:
                    agent.work_efficiency = max(0.1, agent.work_efficiency - 0.05)
