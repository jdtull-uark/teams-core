import mesa
import random
from typing import Any, Dict, List, TYPE_CHECKING
from ..utils import log
import uuid

if TYPE_CHECKING:
    from ..model import EngineeringTeamModel

class BaseAgent(mesa.Agent):
    """Base class for all agents in the engineering team model."""
    
    def __init__(self, model: 'EngineeringTeamModel'):
        super().__init__(model)
        self.name = f"Agent {self.unique_id}" # Display name
        self.attributes: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []

    @property   
    def __dict__(self):
        """Override __dict__ to exclude model reference and include custom fields."""
        original_dict = super().__dict__.copy()
        original_dict['unique_id'] = self.unique_id
        original_dict['attributes'] = self.attributes
        original_dict['history'] = self.history
        # Remove model reference
        return {k: v for k, v in original_dict.items() if k != 'model'}

    def _log_history(self, action: str, details: Dict[str, Any] = None):
        """Log an action taken by the agent to both internal history and file."""
        if details is None:
            details = {}
            
        log_entry = {
            "step": self.model.steps,
            "unique_id": self.unique_id,
            "action": action,
            **details
        }
        self.history.append(log_entry)
        
        log.log_agent_action(
            self.unique_id,
            self.model.steps,
            action,
            details
        )
        
    def initiate_interaction(self, recipient_agent: 'BaseAgent', interaction_type: Any, 
                           details: Dict[str, Any] = None) -> bool:
        """
        Initiate an interaction with another agent.
        Returns True if the interaction was successfully initiated, False otherwise.
        """
        if not recipient_agent:
            self._log_history("interaction_failed_no_recipient", {
                "type": str(interaction_type),
                "details": details or {}
            })
            return False

        if details is None:
            details = {}
            
        if "interaction_duration" not in details:
            details["interaction_duration"] = random.uniform(0.5, 10.0)

        self._log_history("initiate_interaction", {
            "type": str(interaction_type),
            "recipient": recipient_agent.unique_id,
            "details": details
        })
        
        # Send interaction to recipient
        recipient_agent.receive_interaction(self, interaction_type, details)
        return True

    def receive_interaction(self, sender_agent: 'BaseAgent', interaction_type: Any, 
                          details: Dict[str, Any] = None):
        """
        Process an incoming interaction from another agent.
        This method can be overridden by specific agent types to define reactions.
        """
        if details is None:
            details = {}
            
        self._log_history("receive_interaction", {
            "type": str(interaction_type),
            "sender": sender_agent.unique_id,
            "details": details
        })

    def step(self):
        """Standard Mesa step function - override in subclasses."""
        pass