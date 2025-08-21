"""
Core interfaces for the framework.
All extensions should implement these interfaces.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .agent import BaseAgent
    from .model import BaseModel

class AgentBehavior(ABC):
    """Interface for agent behaviors that can be plugged into agents."""
    @abstractmethod
    def execute(self, agent: 'BaseAgent', model: 'BaseModel') -> None:
        pass
    @abstractmethod
    def can_execute(self, agent: 'BaseAgent', model: 'BaseModel') -> bool:
        pass

class InteractionHandler(ABC):
    """Interface for handling interactions between agents."""
    @abstractmethod
    def handle_interaction(self, initiator: 'BaseAgent', recipient: 'BaseAgent', 
                         interaction_type: str, context: Dict[str, Any]) -> bool:
        pass
    @abstractmethod
    def get_supported_types(self) -> List[str]:
        pass

class TaskGenerator(ABC):
    """Interface for generating tasks in the simulation."""
    @abstractmethod
    def generate_task(self, model: 'BaseModel', context: Dict[str, Any] = None) -> Any:
        pass
    @abstractmethod
    def should_generate(self, model: 'BaseModel') -> bool:
        pass

class Rule(ABC):
    """Interface for model-level rules that affect simulation behavior."""
    def preprocess_interaction(self, initiator, recipient, interaction_type: str, context: Any) -> tuple:
        """
        Optionally modify or block an interaction before it occurs.
        Return (allow: bool, possibly modified context: Any).
        By default, allow all interactions and do not modify context.
        Subclasses can override this to implement rule-based impacts.
        """
        return True, context
    
    @abstractmethod
    def apply(self, model: 'BaseModel') -> None:
        pass
    @abstractmethod
    def should_apply(self, model: 'BaseModel') -> bool:
        pass

class Component(ABC):
    """Base interface for all pluggable components."""
    @abstractmethod
    def initialize(self, owner: Any) -> None:
        pass
    @abstractmethod
    def step(self) -> None:
        pass
    
    def soft_reset(self) -> None:
        """
        Perform a soft reset of the component's state.
        This should reset transient state but preserve learned/accumulated data.
        Default implementation does nothing - override in subclasses as needed.
        """
        pass
    
    def close(self) -> None:
        """
        Close/finalize the component when it's no longer needed.
        This should perform cleanup and finalization tasks.
        Default implementation does nothing - override in subclasses as needed.
        """
        pass
