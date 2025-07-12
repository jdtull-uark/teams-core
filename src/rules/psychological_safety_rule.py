from .base import BaseRule
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..model import EngineeringTeamModel

class PsychologicalSafetyRule(BaseRule):
    """
    Rule: If psychological safety >= threshold, then enable / increase collaborative interactions.
    This rule evaluates the current psychological safety level against a defined threshold.
    """
    
    def __init__(self, model: 'EngineeringTeamModel', name: str = "PsychologicalSafetyRule"):
        super().__init__(model, name)
        # This rule interacts with the model's psychological_safety and psychological_safety_threshold attributes.
        
    def evaluate(self, context: Any = None) -> bool:
        """
        Evaluates if the psychological safety condition for collaboration is met.
        For now, it simply checks the model's global psychological safety.
        """
        # The rule checks the model's overall psychological safety
        return self.model.psychological_safety >= self.model.psychological_safety_threshold

    def get_collaboration_factor(self, context: Any = None) -> float:
        """
        Returns a factor (0.0 to 1.0) indicating the strength of psychological safety for collaboration.
        """
        # Calculate a factor based on how far above/below the threshold the safety is.
        # Max(0, ...) ensures it doesn't go below zero. Min(1, ...) ensures it doesn't exceed one.
        safety_ratio = self.model.psychological_safety / self.model.psychological_safety_threshold
        return max(0.0, min(1.0, safety_ratio))