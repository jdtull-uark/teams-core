from typing import Dict, List, Any, TYPE_CHECKING
import random
from enum import StrEnum
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from ..engineer import EngineerAgent

class Interaction:
    """Handles all interaction logic for an engineer agent."""
    
    def __init__(self, agent: 'EngineerAgent'):
        self.agent = agent
        self.interaction_history: List[InteractionRecord] = []
        self.help_requests_made: int = 0
        self.help_requests_received: int = 0
    
    def process_interaction(self, recipient: 'EngineerAgent', interaction_type: Any = None, 
                          speaking_percentage: float = 0, details: Dict[str, Any] = None):
        """Process an interaction with another agent."""
        if details is None:
            details = {}
        
        # Handle specific interaction types
        interaction_type_enum = InteractionType(interaction_type) if interaction_type else None

        if interaction_type_enum == InteractionType.COLLABORATION:
            self.handle_collaboration(recipient, details)
        elif interaction_type_enum == InteractionType.HELP_REQUEST:
            self.handle_help_request(recipient, details)
        elif interaction_type_enum == InteractionType.HELP_OFFER:
            self.handle_help_offer(recipient, details)
        elif interaction_type_enum == InteractionType.KNOWLEDGE_REQUEST:
            self.handle_knowledge_request(recipient, details)
        elif interaction_type_enum == InteractionType.KNOWLEDGE_SHARE:
            self.handle_knowledge_share(recipient, details)
        elif interaction_type_enum == InteractionType.FEEDBACK:
            self.handle_feedback(recipient, details)
        
        # Record the interaction
        interaction_record = InteractionRecord(
            step=self.agent.model.steps,
            initiator_id=str(self.agent.unique_id),
            recipient_id=str(recipient.unique_id),
            interaction_type=interaction_type,
            duration=details.get("interaction_duration", 0),
        )
        self.interaction_history.append(interaction_record)
    
    def receive_interaction(self, sender_agent: 'EngineerAgent', interaction_type: Any = None, 
                          details: Dict[str, Any] = None, **kwargs):
        """Receive an interaction from another agent."""
        if details is None:
            details = {}
        
        # Call parent's receive_interaction if it exists
        if hasattr(super(self.agent.__class__, self.agent), 'receive_interaction'):
            super(self.agent.__class__, self.agent).receive_interaction(sender_agent, interaction_type, details)
        
        # Process the interaction from recipient's perspective
        self.process_interaction(
            sender_agent, 
            interaction_type=interaction_type, 
            speaking_percentage=1 - details.get("sender_speaking_percentage", 0.5), 
            details=details
        )

    def initiate_interaction(self, recipient_agent: 'EngineerAgent', interaction_type: Any, 
                           details: Dict[str, Any] = None):
        """Initiate an interaction with another agent."""
        if details is None:
            details = {}
        
        # Set interaction parameters
        details["interaction_duration"] = random.uniform(1.0, 5.0)
        details["sender_speaking_percentage"] = random.uniform(0.05, 0.95)

        # Call parent's initiate_interaction if it exists
        if hasattr(super(self.agent.__class__, self.agent), 'initiate_interaction'):
            super(self.agent.__class__, self.agent).initiate_interaction(recipient_agent, interaction_type, details)

        # Process the interaction from initiator's perspective
        self.process_interaction(
            recipient_agent, 
            interaction_type=interaction_type, 
            speaking_percentage=details["sender_speaking_percentage"], 
            details=details
        )

    # Interaction Type Handlers
    def handle_collaboration(self, recipient: 'EngineerAgent', details: Dict[str, Any]):
        """Handle collaboration interaction - general knowledge sharing."""
        # Could implement general collaboration logic here
        pass

    def handle_help_request(self, recipient: 'EngineerAgent', details: Dict[str, Any]):
        """Handle help request interaction."""
        self.help_requests_made += 1
        
        # Create knowledge request details
        details = self.create_knowledge_request_details(recipient, details)
        recipient.receive_interaction(self.agent, InteractionType.HELP_REQUEST, details)

    def handle_help_offer(self, recipient: 'EngineerAgent', details: Dict[str, Any]):
        """Handle help offer interaction - proactive knowledge sharing."""
        # Could implement proactive help offering logic
        pass

    def handle_knowledge_request(self, recipient: 'EngineerAgent', details: Dict[str, Any]):
        """Handle knowledge request interaction."""
        details = {
            "interaction_type": InteractionType.KNOWLEDGE_REQUEST,
            "recipient_id": recipient.unique_id,
            "requested_concepts": self.agent.knowledge_manager.get_missing_knowledge(),
            "interaction_duration": details.get("interaction_duration", self.agent.random.uniform(1.0, 5.0)),
            "sender_speaking_percentage": details.get("sender_speaking_percentage", self.agent.random.uniform(0.05, 0.95))
        }
        recipient.receive_interaction(self.agent, InteractionType.KNOWLEDGE_REQUEST, details)

    def handle_knowledge_share(self, recipient: 'EngineerAgent', details: Dict[str, Any]):
        """Handle knowledge sharing interaction."""
        concept = details.get("shared_concept")
        if concept:
            share_details = {
                "interaction_type": InteractionType.KNOWLEDGE_SHARE,
                "recipient_id": recipient.unique_id,
                "shared_concept": concept,
                "interaction_duration": details.get("interaction_duration", 2.0),
                "sender_speaking_percentage": details.get("sender_speaking_percentage", 0.7)
            }  
            recipient.receive_interaction(self.agent, InteractionType.KNOWLEDGE_SHARE, share_details)

    def handle_feedback(self, recipient: 'EngineerAgent', details: Dict[str, Any]):
        """Handle feedback interaction - performance and knowledge feedback."""
        # Could implement feedback logic here
        pass


    def receive_knowledge_request(self, sender: 'EngineerAgent', details: Dict[str, Any]):
        """Receive a knowledge request from another agent."""
        self.help_requests_received += 1
        requested_concepts = details.get("requested_concepts", [])
        
        for concept in requested_concepts:
            if concept in self.agent.knowledge_manager.learned_knowledge:
                # If we know the concept, initiate a knowledge share
                share_details = {
                    "shared_concept": concept,
                    "interaction_duration": details.get("interaction_duration", 2.0),
                    "sender_speaking_percentage": 0.7  # We do most of the talking when sharing
                }
                self.initiate_interaction(sender, InteractionType.KNOWLEDGE_SHARE, share_details)
            elif self.agent.knowledge_manager.knows_agent_with_knowledge(concept):
                # If we know an agent has this knowledge, update the requester's network
                agents_with_knowledge = self.agent.knowledge_manager.get_agents_with_knowledge(concept)
                for unique_id in agents_with_knowledge:
                    sender.knowledge_manager.update_knowledge_network(unique_id, concept)
            else:
                # Share a random concept we know as a consolation
                if self.agent.knowledge_manager.learned_knowledge:
                    random_concept = random.choice(list(self.agent.knowledge_manager.learned_knowledge))
                    sender.knowledge_manager.update_knowledge_network(self.agent.unique_id, random_concept)
  

    def receive_knowledge_share(self, sender: 'EngineerAgent', details: Dict[str, Any]):
        """Receive a knowledge share from another agent."""
        concept = details.get("shared_concept")
        if concept:
            # Receive the shared knowledge
            self.agent.knowledge_manager.receive_shared_knowledge(sender.unique_id, concept)
            # Update our knowledge of what the sender knows
            self.agent.knowledge_manager.update_knowledge_network(sender.unique_id, concept)

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
    knowledge_shared: List[str] = field(default_factory=list)