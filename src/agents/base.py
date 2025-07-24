import mesa
import random
from typing import Any, Dict, List, TYPE_CHECKING
from ..utils import log

if TYPE_CHECKING:
    from ..model import EngineeringTeamModel

class BaseAgent(mesa.Agent):
    """Base class for all agents in the engineering team model."""
    
    def __init__(self, unique_id: int, model: 'EngineeringTeamModel'): # Keep as string literal for forward reference
        super().__init__(model)
        self.unique_id = unique_id
        self.name = f"Agent {unique_id}"
        self.attributes: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []

    @property
    def __dict__(self):
        original_dict = super().__dict__
        original_dict['unique_id'] = self.unique_id
        original_dict['attributes'] = self.attributes
        original_dict['history'] = self.history
        return {k: v for k, v in original_dict.items() if k != 'model'}

    def _log_history(self, action: str, details: Dict[str, Any] = None):
        """Logs an action taken by the agent to both internal history and file."""
        log_entry = {"step": self.model.steps, "action": action}
        if details:
            log_entry.update(details)
        self.history.append(log_entry)
        
        log.log_agent_action(
            self.unique_id,
            self.model.steps,
            action,
            details
        )
        
    def initiate_interaction(self, recipient_agent: 'BaseAgent', interaction_type: Any, details: Dict[str, Any] = None) -> bool:
        """
        Initiates an interaction with another agent.
        This method itself doesn't check psychological safety; the calling agent decides based on its own state.
        Returns True if the interaction was successfully initiated (i.e., logged and sent), False otherwise.
        """

        if recipient_agent:
            if details is None:
                details = {}
            if "interaction_duration" not in details:
                details["interaction_duration"] = random.uniform(0.5, 10)

            self._log_history("initiate_interaction", {
                "type": str(interaction_type),
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