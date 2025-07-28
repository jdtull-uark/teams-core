"""
Core interfaces for the framework.
All extensions should implement these interfaces.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .core.agent import BaseAgent
    from .core.model import BaseModel

class AgentBehavior(ABC):
    """Interface for agent behaviors that can be plugged into agents."""
    
    @abstractmethod
    def execute(self, agent: 'BaseAgent', model: 'BaseModel') -> None:
        """Execute the behavior for the given agent."""
        pass
    
    @abstractmethod
    def can_execute(self, agent: 'BaseAgent', model: 'BaseModel') -> bool:
        """Check if this behavior can be executed by the agent."""
        pass

class InteractionHandler(ABC):
    """Interface for handling interactions between agents."""
    
    @abstractmethod
    def handle_interaction(self, initiator: 'BaseAgent', recipient: 'BaseAgent', 
                         interaction_type: str, context: Dict[str, Any]) -> bool:
        """Handle an interaction between two agents. Returns True if successful."""
        pass
    
    @abstractmethod
    def get_supported_types(self) -> List[str]:
        """Return list of interaction types this handler supports."""
        pass

class TaskGenerator(ABC):
    """Interface for generating tasks in the simulation."""
    
    @abstractmethod
    def generate_task(self, model: 'BaseModel', context: Dict[str, Any] = None) -> Any:
        """Generate a new task."""
        pass
    
    @abstractmethod
    def should_generate(self, model: 'BaseModel') -> bool:
        """Determine if a new task should be generated."""
        pass

class Rule(ABC):
    """Interface for model-level rules that affect simulation behavior."""
    
    @abstractmethod
    def apply(self, model: 'BaseModel') -> None:
        """Apply the rule to the model."""
        pass
    
    @abstractmethod
    def should_apply(self, model: 'BaseModel') -> bool:
        """Determine if the rule should be applied."""
        pass

class Component(ABC):
    """Base interface for all pluggable components."""
    
    @abstractmethod
    def initialize(self, owner: Any) -> None:
        """Initialize the component with its owner."""
        pass
    
    @abstractmethod
    def step(self) -> None:
        """Execute one simulation step for this component."""
        pass