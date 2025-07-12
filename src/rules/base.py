from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..model import EngineeringTeamModel

class BaseRule(ABC):
    """
    Abstract base class for all rules in the simulation.
    Rules encapsulate conditions and potential effects on agents or the model.
    """
    
    def __init__(self, model: 'EngineeringTeamModel', name: str):
        self.model = model
        self.name = name

    @abstractmethod
    def evaluate(self, context: Any = None) -> Any:
        """
        Evaluates the rule's conditions based on the provided context (e.g., an agent,
        or the model's current state).
        Returns a result based on the rule's logic (e.g., boolean, a calculated value).
        Subclasses must implement this.
        """
        pass

    def __str__(self):
        return f"Rule: {self.name}"