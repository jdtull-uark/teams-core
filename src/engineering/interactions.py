"""
Engineering-specific interaction handlers.
"""

import random
from typing import List
from ..framework.interfaces import InteractionHandler
from ..framework.core.agent import BaseAgent

class KnowledgeShareHandler(InteractionHandler):
    """Handles knowledge sharing interactions between agents."""
    
    def get_supported_types(self) -> List[str]:
        return ["knowledge_request", "knowledge_share", "collaboration"]
    
    def handle_interaction(self, initiator: BaseAgent, recipient: BaseAgent, 
                          interaction_type: str, context: dict) -> bool:
        """Handle knowledge-related interactions."""
        
        if interaction_type == "knowledge_request":
            return self._handle_knowledge_request(initiator, recipient, context)
        elif interaction_type == "knowledge_share":
            return self._handle_knowledge_share(initiator, recipient, context)
        elif interaction_type == "collaboration":
            return self._handle_collaboration(initiator, recipient, context)
        
        return False
    
    def _handle_knowledge_request(self, initiator, recipient, context):
        """Handle a request for knowledge."""
        initiator_knowledge = initiator.get_component("knowledge_manager")
        recipient_knowledge = recipient.get_component("knowledge_manager")
        
        if not all([initiator_knowledge, recipient_knowledge]):
            return False
        
        # Determine what knowledge is being requested
        task_manager = initiator.get_component("task_manager")
        if task_manager and task_manager.current_subtask:
            requested_knowledge = initiator_knowledge.get_missing_knowledge(
                task_manager.current_subtask.required_knowledge
            )
        else:
            requested_knowledge = []
        
        if requested_knowledge:
            shareable = recipient_knowledge.get_shareable_knowledge(requested_knowledge)
            if shareable:
                shared_concept = random.choice(shareable)
                initiator_knowledge.receive_shared_knowledge(
                    str(recipient.unique_id), shared_concept
                )
                recipient.log_action("knowledge_shared", {
                    "recipient": initiator.unique_id,
                    "concept": shared_concept
                })
                return True
        
        return False
    
    def _handle_knowledge_share(self, initiator, recipient, context):
        """Handle sharing of specific knowledge."""
        if "shared_knowledge" not in context:
            return False
        
        recipient_knowledge = recipient.get_component("knowledge_manager")
        if recipient_knowledge:
            concept = context["shared_knowledge"]
            return recipient_knowledge.receive_shared_knowledge(
                str(initiator.unique_id), concept
            )
        
        return False
    
    def _handle_collaboration(self, initiator, recipient, context):
        """Handle collaborative knowledge sharing."""
        initiator_knowledge = initiator.get_component("knowledge_manager")
        recipient_knowledge = recipient.get_component("knowledge_manager")
        
        if not all([initiator_knowledge, recipient_knowledge]):
            return False
        
        # Share random knowledge with each other
        success = False
        
        if initiator_knowledge.learned_knowledge:
            shared_concept = random.choice(list(initiator_knowledge.learned_knowledge))
            if recipient_knowledge.receive_shared_knowledge(
                str(initiator.unique_id), shared_concept
            ):
                success = True
        
        if recipient_knowledge.learned_knowledge:
            shared_concept = random.choice(list(recipient_knowledge.learned_knowledge))
            if initiator_knowledge.receive_shared_knowledge(
                str(recipient.unique_id), shared_concept
            ):
                success = True
        
        return success

class HelpRequestHandler(InteractionHandler):
    """Handles help requests between agents."""
    
    def get_supported_types(self) -> List[str]:
        return ["help_request", "help_offer"]
    
    def handle_interaction(self, initiator: BaseAgent, recipient: BaseAgent, 
                          interaction_type: str, context: dict) -> bool:
        """Handle help-related interactions."""
        
        if interaction_type == "help_request":
            return self._handle_help_request(initiator, recipient, context)
        elif interaction_type == "help_offer":
            return self._handle_help_offer(initiator, recipient, context)
        
        return False
    
    def _handle_help_request(self, initiator, recipient, context):
        """Handle a request for help."""
        recipient_comm = recipient.get_component("communication_manager")
        
        if (hasattr(recipient, 'is_available') and recipient.is_available and
            hasattr(recipient, 'motivation') and recipient.motivation >= 0.7):
            
            if recipient_comm:
                recipient_comm.help_requests_received += 1
            
            recipient.log_action("help_request_accepted", {
                "from": initiator.unique_id
            })
            return True
        else:
            recipient.log_action("help_request_denied", {
                "from": initiator.unique_id
            })
            return False
    
    def _handle_help_offer(self, initiator, recipient, context):
        """Handle an offer of help."""
        recipient_knowledge = recipient.get_component("knowledge_manager")
        recipient_task = recipient.get_component("task_manager")
        recipient_comm = recipient.get_component("communication_manager")
        
        # Accept help if we need it
        need_help = (
            (recipient_comm and recipient_comm.seeking_knowledge) or
            (recipient_knowledge and recipient_task and 
             recipient_task.current_subtask and
             not recipient_knowledge.has_all_required_knowledge(
                 recipient_task.current_subtask.required_knowledge
             ))
        )
        
        if need_help:
            recipient.log_action("help_offer_accepted", {
                "from": initiator.unique_id
            })
            return True
        else:
            recipient.log_action("help_offer_declined", {
                "from": initiator.unique_id
            })
            return False