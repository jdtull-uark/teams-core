from .base import BaseRule
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..model import EngineeringTeamModel
    from ..agents import EngineerAgent, ManagerAgent

class PsychologicalSafetyRule(BaseRule):
    """
    Rule: If psychological safety >= threshold, then enable / increase collaborative interactions.
    This rule evaluates the current psychological safety level against a defined threshold.
    """
    
    def __init__(self, model: 'EngineeringTeamModel', name: str = "PsychologicalSafetyRule"):
        super().__init__(model, name)
        
    def evaluate(self, agent_one: 'EngineerAgent' = None, agent_two: 'EngineerAgent' = None, context: Any = None) -> bool:
        """
        Evaluates if the psychological safety condition for collaboration is met.
        """
        if agent_one and agent_two:
            return ( (agent_one.pps + agent_two.pps) / 2) >= self.model.psychological_safety_threshold
        else:
            return self.model.psychological_safety

    def get_collaboration_factor(self, context: Any = None) -> float:
        """
        Returns a factor (0.0 to 1.0) indicating the strength of psychological safety for collaboration.
        """
        # Calculate a factor based on how far above/below the threshold the safety is.
        # Max(0, ...) ensures it doesn't go below zero. Min(1, ...) ensures it doesn't exceed one.
        safety_ratio = self.model.psychological_safety / self.model.psychological_safety_threshold
        return max(0.0, min(1.0, safety_ratio))