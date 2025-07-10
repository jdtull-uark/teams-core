import mesa
from typing import Any, Dict, List, TYPE_CHECKING # NEW: Import TYPE_CHECKING

if TYPE_CHECKING:
    from ..model import EngineeringTeamModel

class BaseAgent(mesa.Agent):
    """Base class for all agents in the engineering team model."""
    
    def __init__(self, unique_id: int, model: 'EngineeringTeamModel'): # Keep as string literal for forward reference
        super().__init__(model)
        self.attributes: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []

    def _log_history(self, action: str, details: Dict[str, Any] = None):
        """Logs an action taken by the agent."""
        log_entry = {"step": self.model.schedule.steps, "action": action}
        if details:
            log_entry.update(details)
        self.history.append(log_entry)
        
    def initiate_interaction(self, recipient_agent: 'BaseAgent', interaction_type: Any, details: Dict[str, Any] = None) -> bool: # interaction_type needs proper import or Any
        """
        Initiates an interaction with another agent.
        This method itself doesn't check psychological safety; the calling agent decides based on its own state.
        Returns True if the interaction was successfully initiated (i.e., logged and sent), False otherwise.
        """
        
        if recipient_agent:
            self._log_history("initiate_interaction", {
                "type": str(interaction_type), # Cast to string since it's not a proper enum without types.py changes
                "recipient": recipient_agent.unique_id,
                "details": details
            })
            recipient_agent.receive_interaction(self, interaction_type, details)
            return True
        else:
            self._log_history("interaction_failed_no_recipient", {
                "type": str(interaction_type),
                "details": details
            })
            return False

    def receive_interaction(self, sender_agent: 'BaseAgent', interaction_type: Any, details: Dict[str, Any] = None):
        """
        Processes an incoming interaction from another agent.
        This method can be overridden by specific agent types to define reactions.
        """
        self._log_history("receive_interaction", {
            "type": str(interaction_type),
            "sender": sender_agent.unique_id,
            "details": details
        })

    def step(self):
        """Standard Mesa step function."""
        pass