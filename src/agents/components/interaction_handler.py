from typing import List, Dict, Any, Optional, Required, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import StrEnum
from ...utils import log
import random

if TYPE_CHECKING:
    from ..engineer import EngineerAgent

class Communicator:
    """Handles all interaction logic for an engineer agent."""
    
    def __init__(self, agent: 'EngineerAgent'):
        self.agent = agent
        self.interaction_history: List[InteractionRecord] = []
        self.help_requests_made: int = 0
        self.help_requests_received: int = 0
    
    def initiate_interaction(self, recipient_agent: 'EngineerAgent', interaction_type, details: Dict[str, Any] = None):
        if not details:
            details = {}
        
        details["sender_agent"] = self.agent
        details["recipient_agent"] = recipient_agent
        details["interaction_type"] = interaction_type
        details["interaction_duration"] = random.uniform(0.5, 10)

        self.agent.log_interaction(status="sent", details=details)

    def receive_interaction(self, sender_agent: 'EngineerAgent', interaction_type, details: Dict[str, Any] = None):
        if not details:
            return

        match interaction_type:
            case InteractionType.COLLABORATION:
                self.handle_collaboration(sender_agent=sender_agent, details=details)
            case InteractionType.KNOWLEDGE_REQUEST:
                self.handle_knowledge_request(sender_agent=sender_agent, details=details)
            case InteractionType.KNOWLEDGE_SHARE:
                self.handle_knowledge_share(sender_agent=sender_agent, details=details)
            case InteractionType.HELP_REQUEST:
                self.handle_help_request(sender_agent=sender_agent, details=details)
            case InteractionType.HELP_OFFER:
                self.handle_help_offer(sender_agent=sender_agent, details=details)
            case InteractionType.FEEDBACK:
                self.handle_feedback(sender_agent=sender_agent, details=details)
            case _:
                return

    def handle_collaboration(self, sender_agent: 'EngineerAgent', details: Dict[str, Any]):
        sender_agent.receive_shared_knowledge(self.agent.unique_id, random.choice(self.agent.learned_knowledge))
        self.receive_shared_knowledge(sender_agent.unique_id, random.choice(sender_agent.learned_knowledge))

    def handle_knowledge_request(self, sender_agent: 'EngineerAgent', details: Dict[str, Any]):
        if 'requested_knowledge' not in details:
            return
        
        if self.agent.get_shareable_knowledge(details['requested_knowledge']):
            self.initiate_interaction(sender_agent, 'knowledge_share', details={'shared_knowledge': random.choice(self.agent.get_shareable_knowledge(details['requested_knowledge']))})
        

    def handle_knowledge_share(self, sender_agent: 'EngineerAgent', details: Dict[str, Any]):
        if 'shared_knowledge' not in details:
            return
        
        self.agent.receive_shared_knowledge(sender_agent.unique_id, details['shared_knowledge'])
        self.agent.add_agent_knowledge(sender_agent.unique_id, details["shared_knowledge"])

    def handle_help_request(self, sender_agent: 'EngineerAgent', details: Dict[str, Any]):
        pass

    def handle_help_offer(self, sender_agent: 'EngineerAgent', details: Dict[str, Any]):
        pass

    def handle_feedback(self, sender_agent: 'EngineerAgent', details: Dict[str, Any]):
        pass


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
