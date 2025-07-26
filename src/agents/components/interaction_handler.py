from typing import List, Dict, Any, Optional, Required, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import StrEnum
from ...utils import log
import random

if TYPE_CHECKING:
    from ..engineer import EngineerAgent

class InteractionHandler:
    """Handles all interaction logic for an engineer agent."""
    
    def __init__(self, agent: 'EngineerAgent'):
        self.agent = agent
        self.interaction_history: List[InteractionRecord] = []
        self.help_requests_made: int = 0
        self.help_requests_received: int = 0
    
    def initiate_interaction(self, recipient_agent: 'EngineerAgent', interaction_type, details: Dict[str, Any] = None):
        if not details:
            details = {}
        
        details["recipient_agent"] = recipient_agent
        details["interaction_type"] = interaction_type
        details["interaction_duration"] = random.uniform(0.5, 10)

    def receive_interaction(self, sender_agent: 'EngineerAgent', interaction_type, details: Dict[str, Any] = None):
        pass

   # TODO: Implement this stuff again


    def get_interaction_stats(self) -> Dict[str, Any]:
        """Get statistics about this agent's interactions."""
        return {
            "total_interactions": len(self.interaction_history),
            "help_requests_made": self.help_requests_made,
            "help_requests_received": self.help_requests_received,
            "recent_interactions": self.interaction_history[-10:] if self.interaction_history else []
        }
    
class InteractionType(StrEnum):
    COLLABORATION = "collaboration"
    HELP_REQUEST = "help_request"
    HELP_OFFER = "help_offer"
    KNOWLEDGE_REQUEST = "knowledge_request"
    KNOWLEDGE_SHARE = "knowledge_share"
    FEEDBACK = "feedback"

@dataclass
class InteractionRecord:
    """Records details of an interaction between agents."""
    step: int
    initiator_id: str
    recipient_id: str
    interaction_type: InteractionType
    duration: float
    details: Dict[str, Any] = field(default_factory=dict)
