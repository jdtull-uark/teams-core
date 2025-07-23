from typing import List, Dict, Any, Optional, Required, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import StrEnum
from ...utils import log
import random

if TYPE_CHECKING:
    from ..engineer import EngineerAgent

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

class InteractionMixin:
    def __init__(self, model):
        pass

    def initiate_interaction(self, *, recipient_agent: 'EngineerAgent', interaction_type: InteractionType, details: Dict[str, Any] = {}):
        """Initiate an interaction with another agent."""
        if details is None:
            details = {}
        details["sender_agent"] = self
        details["recipient_agent"] = recipient_agent.name
        details["interaction_duration"] = random.uniform(0.5, 10)
        
        self.log_interaction(status = "sent", details = details)
        recipient_agent.receive_interaction(details = details)

    def receive_interaction(self, sender_agent: 'EngineerAgent', interaction_type: Any = None, details: Dict[str, Any] = None, **kwargs):
        """Receive an interaction from another agent."""
        self.log_interaction(status = "received", details = details)
        self.process_interaction(details = details)

    def process_interaction(self, recipient: 'EngineerAgent', interaction_type: Any = None, speaking_percentage: int = 0, details: Dict[str, Any] = None):
        """Process an interaction with another agent."""
        pass
    
    
    def handle_collaboration(self, recipient: 'EngineerAgent', details: Dict[str, Any]):
        """Handle collaboration interaction - general knowledge sharing."""
        pass
    
    def handle_help_request(self, recipient: 'EngineerAgent', details: Dict[str, Any]):
        """Handle help request interaction."""
        pass
    
    def handle_help_offer(self, recipient: 'EngineerAgent', details: Dict[str, Any]):
        """Handle help offer interaction - proactive knowledge sharing."""
        pass

    def initiate_knowledge_request(self, recipient: 'EngineerAgent', details: Dict[str, Any]) -> Dict[str, Any]:
        """Initiate a knowledge request interaction. Should return interaction details."""
        pass
    
    def receive_knowledge_request(self, sender: 'EngineerAgent', details: Dict[str, Any]):
        """Receive a knowledge request from another agent."""
        pass
        
    def handle_knowledge_request(self, recipient: 'EngineerAgent', details: Dict[str, Any]):
        """Handle knowledge sharing interaction."""
        pass

    def initiate_knowledge_share(self, recipient: 'EngineerAgent', details: Dict[str, Any]) -> Dict[str, Any]:
        """Initiate a knowledge share interaction."""
        pass
    
    def receive_knowledge_share(self, sender: 'EngineerAgent', details: Dict[str, Any]):
        """Receive a knowledge share from another agent."""
        pass

    def handle_knowledge_share(self, recipient: 'EngineerAgent', details: Dict[str, Any]):
        """Handle knowledge sharing interaction."""
        pass
    
    def handle_feedback(self, recipient: 'EngineerAgent', details: Dict[str, Any]):
        """Handle feedback interaction - performance and knowledge feedback."""
        pass