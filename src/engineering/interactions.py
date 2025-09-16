"""
Engineering-specific interaction handlers.
"""

import random
from typing import List
from ..framework.core.interfaces import InteractionHandler
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
        

        initiator.log_action("knowledge_requested", {
            "recipient": recipient.unique_id,
            "requested_knowledge": requested_knowledge,
            "has_current_task": bool(task_manager and task_manager.current_subtask)
        })
        
        if requested_knowledge:
            shareable = recipient_knowledge.get_shareable_knowledge(requested_knowledge)
            if shareable:
                shared_concept = random.choice(shareable)
                if 'knowledge_share_modifier' in context:
                    initiator_knowledge.receive_partial_shared_knowledge(
                        str(recipient.unique_id), shared_concept, context['knowledge_share_modifier']
                    )
                    recipient.log_action("partial_knowledge_shared", {
                        "recipient": initiator.unique_id,
                        "concept": shared_concept,
                        "modifier": context['knowledge_share_modifier']
                    })
                else:
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
        return ["performance_evaluation"]
    
    def handle_interaction(self, initiator: BaseAgent, recipient: BaseAgent, 
                          interaction_type: str, context: dict) -> bool:
        """Handle performance evaluation interactions."""
        
        if interaction_type == "performance_evaluation":
            return self._handle_performance_evaluation(initiator, recipient, context)
        
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
        
        # Log the evaluation for debugging
        initiator.log_action("performance_evaluation", {
            "performance_ratio": performance_ratio,
            "recipient_id": recipient.unique_id if recipient else None,
            "old_team_efficacy": getattr(initiator, 'perceived_team_efficacy', 0.5)
        })
        
        # Update team efficacy based on observed performance
        if hasattr(initiator, 'perceived_team_efficacy'):
            old_efficacy = initiator.perceived_team_efficacy
            
            # Enhanced performance evaluation with rewards for exceptional performance
            if performance_ratio > 1.2:  # Exceptional performance (20% faster than required)
                boost = 0.3  # Larger boost for exceptional performance
            elif performance_ratio > 1.0:  # Above average performance
                boost = 0.2  # Standard boost for good performance
            elif performance_ratio > 0.55:  # Decent performance
                boost = 0.1  # Small boost for acceptable performance
            elif performance_ratio < 0.45:  # Poor performance
                boost = -0.1  # Penalty for poor performance
            elif performance_ratio < 0.25:
                boost = -.2
            else:
                boost = 0.0  # No change for average performance
            
            pps_modifier = initiator.perceived_psychological_safety * 2 - 1
            initiator.perceived_team_efficacy = max(0.0, min(1.0, initiator.perceived_team_efficacy + boost + pps_modifier))
            
            # Log the change
            if old_efficacy != initiator.perceived_team_efficacy:
                initiator.log_action("team_efficacy_updated", {
                    "old_value": old_efficacy,
                    "new_value": initiator.perceived_team_efficacy,
                    "change": initiator.perceived_team_efficacy - old_efficacy,
                    "performance_ratio": performance_ratio
                })
        
        # If there's a recipient, they also update their perception (smaller effect)
        if recipient and hasattr(recipient, 'perceived_team_efficacy'):
            old_efficacy = recipient.perceived_team_efficacy
            
            # Observer gets smaller but similar updates
            if performance_ratio > 1.2:  # Exceptional performance observed
                boost = 0.04  # Half the effect for observers
            elif performance_ratio > 1.0:  # Above average performance observed
                boost = 0.025
            elif performance_ratio > 0.7:  # Decent performance observed
                boost = 0.01
            elif performance_ratio < 0.3:  # Poor performance observed
                boost = -0.02
            else:  # Average performance
                boost = 0.0
            
            pps_modifier = recipient.perceived_psychological_safety * 2 - 1
            recipient.perceived_team_efficacy = max(0.0, min(1.0, recipient.perceived_team_efficacy + boost + pps_modifier))
            
            # Log the change
            if old_efficacy != recipient.perceived_team_efficacy:
                recipient.log_action("team_efficacy_updated_observer", {
                    "old_value": old_efficacy,
                    "new_value": recipient.perceived_team_efficacy,
                    "change": recipient.perceived_team_efficacy - old_efficacy,
                    "observed_performance": performance_ratio,
                    "evaluator_id": initiator.unique_id
                })
        
        return True
    
    def _calculate_performance_ratio(self, agent):
        """Calculate performance ratio based on task grading system."""
        task_manager = agent.get_component("task_manager")
        if not task_manager:
            return 0.5
        
        # Access the current step from the agent's model
        current_step = agent.model.step_count
        
        # Get completed tasks for evaluation
        completed_tasks = getattr(task_manager, 'completed_tasks', [])
        current_task = getattr(task_manager, 'current_task', None)
        
        # Collect grades from completed tasks and current task
        grades = []
        
        # Grade completed tasks (use last 5 for recent performance)
        for task in completed_tasks[-5:]:
            grade = task.grade(current_step)
            if grade > 0:  # Only include valid grades
                grades.append(grade)
        
        # If we have a current task in progress, include its grade too
        if current_task:
            current_grade = current_task.grade(current_step)
            if current_grade > 0:
                grades.append(current_grade)
        
        # Calculate average performance ratio
        if grades:
            avg_grade = sum(grades) / len(grades)
            return avg_grade
        else:
            # No gradeable tasks - return neutral performance
            return 0.8  # Slightly below average for agents with no completed work