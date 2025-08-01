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


class PerformanceEvaluationHandler(InteractionHandler):
    """Handles performance evaluation interactions that update team efficacy."""
    
    def get_supported_types(self) -> List[str]:
        return ["performance_evaluation", "team_feedback"]
    
    def handle_interaction(self, initiator: BaseAgent, recipient: BaseAgent, 
                          interaction_type: str, context: dict) -> bool:
        """Handle performance evaluation interactions."""
        
        if interaction_type == "performance_evaluation":
            return self._handle_performance_evaluation(initiator, recipient, context)
        elif interaction_type == "team_feedback":
            return self._handle_team_feedback(initiator, recipient, context)
        
        return False
    
    def _handle_performance_evaluation(self, initiator, recipient, context):
        """Handle performance evaluation based on task completion vs difficulty."""
        # Get task managers for both agents
        initiator_task_manager = initiator.get_component("task_manager")
        recipient_task_manager = recipient.get_component("task_manager")
        
        if not initiator_task_manager:
            return False
        
        # Calculate performance metrics
        performance_ratio = self._calculate_performance_ratio(initiator)
        
        # Update team efficacy based on observed performance
        if hasattr(initiator, 'perceived_team_efficacy'):
            # Positive performance increases team efficacy perception
            if performance_ratio > 0.7:
                initiator.perceived_team_efficacy = min(1.0, 
                    initiator.perceived_team_efficacy + 0.05)
            elif performance_ratio < 0.3:
                initiator.perceived_team_efficacy = max(0.0, 
                    initiator.perceived_team_efficacy - 0.03)
        
        # If there's a recipient, they also update their perception
        if recipient and hasattr(recipient, 'perceived_team_efficacy'):
            if performance_ratio > 0.7:
                recipient.perceived_team_efficacy = min(1.0, 
                    recipient.perceived_team_efficacy + 0.02)
            elif performance_ratio < 0.3:
                recipient.perceived_team_efficacy = max(0.0, 
                    recipient.perceived_team_efficacy - 0.02)
        
        return True
    
    def _handle_team_feedback(self, initiator, recipient, context):
        """Handle general team feedback interactions."""
        feedback_type = context.get("feedback_type", "neutral")
        
        # Update team efficacy based on feedback
        if hasattr(initiator, 'perceived_team_efficacy'):
            if feedback_type == "positive":
                initiator.perceived_team_efficacy = min(1.0, 
                    initiator.perceived_team_efficacy + 0.03)
            elif feedback_type == "negative":
                initiator.perceived_team_efficacy = max(0.0, 
                    initiator.perceived_team_efficacy - 0.02)
        
        return True
    
    def _calculate_performance_ratio(self, agent):
        """Calculate performance ratio based on task completion vs difficulty."""
        task_manager = agent.get_component("task_manager")
        if not task_manager:
            return 0.5
        
        # Get completed tasks and their difficulty
        completed_tasks = getattr(task_manager, 'completed_tasks', [])
        if not completed_tasks:
            return 0.5
        
        # Calculate average performance (this is a simplified metric)
        total_performance = 0
        task_count = 0
        
        for task in completed_tasks[-5:]:  # Look at last 5 tasks
            if hasattr(task, 'difficulty') and hasattr(task, 'completion_time'):
                # Higher difficulty with faster completion = better performance
                expected_time = task.difficulty * 10  # Simple heuristic
                actual_time = getattr(task, 'completion_time', expected_time)
                
                if actual_time > 0:
                    performance = min(2.0, expected_time / actual_time)
                    total_performance += performance
                    task_count += 1
        
        if task_count > 0:
            return min(1.0, total_performance / task_count / 2.0)
        
        return 0.5