import mesa
import random
from typing import Any, Dict, List, TYPE_CHECKING
from ..utils import log

if TYPE_CHECKING:
    from ..model import EngineeringTeamModel

class BaseAgent(mesa.Agent):
    """Base class for all agents in the engineering team model."""
    
    def __init__(self, model: 'EngineeringTeamModel'): # Keep as string literal for forward reference
        super().__init__(model)
        self.name = f"Agent {self.unique_id}"
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
        
    def log_interaction(self, status: str = 'unknown', details: Dict[str, Any] = None) -> bool:
        """
        Logs an interaction with another agent.
        This method itself doesn't check psychological safety; the calling agent decides based on its own state.
        Returns True if the interaction was successfully initiated (i.e., logged and sent), False otherwise.
        """

        self._log_history("interaction", {
            "status": status,
            "details": details
        })

    def step(self):
        """Standard Mesa step function."""
        pass