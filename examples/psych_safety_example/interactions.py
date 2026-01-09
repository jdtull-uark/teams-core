"""Performance evaluation interaction handler."""

from typing import List
from src.framework.core.interfaces import InteractionHandler
from src.framework.core.agent import BaseAgent

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
