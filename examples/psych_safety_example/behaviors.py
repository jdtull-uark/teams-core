"""Evaluation behavior for performance assessment."""

import random
from typing import TYPE_CHECKING
from src.framework.core.interfaces import AgentBehavior

if TYPE_CHECKING:
    from src.framework.core.agent import BaseAgent
    from src.framework.core.model import BaseModel

class EvaluationBehavior(AgentBehavior):
    """Behavior for agents to evaluate team members' performance."""
    
    def __init__(self, evaluation_frequency: float = 0.5):
        """
        Initialize evaluation behavior.
        
        Args:
            evaluation_frequency: Probability of performance evaluation per step (default 50%)
        """
        self.evaluation_frequency = evaluation_frequency
    
    def can_execute(self, agent: 'BaseAgent', model: 'BaseModel') -> bool:
        """Check if agent can conduct evaluations."""
        # Agent should have reasonable communication skills and motivation
        return (hasattr(agent, 'communication_skill') and agent.communication_skill > 0.2 and
                hasattr(agent, 'motivation') and agent.motivation > 0.3 and
                hasattr(model, 'space') and agent.position is not None)
    
    def execute(self, agent: 'BaseAgent', model: 'BaseModel') -> None:
        """Execute evaluation behavior."""
        # Get nearby agents
        if not hasattr(model, 'space'):
            return
            
        neighbors = model.space.get_neighbors(
            agent.position, moore=True, include_center=False, radius=2
        )
        
        if not neighbors:
            return
        
        rand = random.random()
        interaction_type = None
        
        if rand < self.evaluation_frequency:
            interaction_type = "performance_evaluation"
        
        if interaction_type:
            # Choose a random neighbor to evaluate
            target_agent = random.choice(neighbors)
            
            if hasattr(target_agent, 'communication_skill'):
                success = agent.interact_with(target_agent, interaction_type)
                
                if success:
                    agent.log_action(f"{interaction_type}_initiated", {
                        "target_agent": target_agent.unique_id,
                        "step": model.step_count
                    })
