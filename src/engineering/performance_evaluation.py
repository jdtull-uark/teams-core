"""
Performance evaluation interaction handler for team efficacy tracking.
"""

import random
from typing import List, Dict, Any
from ..framework.interfaces import InteractionHandler
from ..framework.core.agent import BaseAgent

class PerformanceEvaluationHandler(InteractionHandler):
    """Handles performance evaluation interactions between agents."""
    
    def get_supported_types(self) -> List[str]:
        return ["performance_evaluation", "check_in"]
    
    def handle_interaction(self, initiator: BaseAgent, recipient: BaseAgent, 
                          interaction_type: str, context: Dict[str, Any]) -> bool:
        """Handle performance evaluation interactions."""
        
        if interaction_type == "performance_evaluation":
            return self._handle_performance_evaluation(initiator, recipient, context)
        elif interaction_type == "check_in":
            return self._handle_check_in(initiator, recipient, context)
        
        return False
    
    def _handle_performance_evaluation(self, initiator: BaseAgent, recipient: BaseAgent, context: Dict[str, Any]) -> bool:
        """Handle a formal performance evaluation interaction."""
        # Get performance metrics for both agents
        initiator_performance = self._calculate_performance_metrics(initiator)
        recipient_performance = self._calculate_performance_metrics(recipient)
        
        # Both agents evaluate each other
        success = False
        
        if self._update_team_efficacy_perception(initiator, recipient_performance):
            success = True
            
        if self._update_team_efficacy_perception(recipient, initiator_performance):
            success = True
        
        # Log the evaluation
        if success:
            initiator.log_action("performance_evaluation_conducted", {
                "evaluated_agent": recipient.unique_id,
                "recipient_performance": recipient_performance,
                "step": initiator.model.step_count
            })
            
            recipient.log_action("performance_evaluation_received", {
                "evaluating_agent": initiator.unique_id,
                "initiator_performance": initiator_performance,
                "step": recipient.model.step_count
            })
        
        return success
    
    def _handle_check_in(self, initiator: BaseAgent, recipient: BaseAgent, context: Dict[str, Any]) -> bool:
        """Handle a casual check-in interaction."""
        # Lighter version of performance evaluation
        initiator_performance = self._calculate_simple_performance(initiator)
        recipient_performance = self._calculate_simple_performance(recipient)
        
        # Update perceptions with less weight than formal evaluation
        success = False
        
        if self._update_team_efficacy_perception(initiator, recipient_performance, weight=0.3):
            success = True
            
        if self._update_team_efficacy_perception(recipient, initiator_performance, weight=0.3):
            success = True
        
        # Log the check-in
        if success:
            initiator.log_action("check_in_conducted", {
                "checked_agent": recipient.unique_id,
                "step": initiator.model.step_count
            })
        
        return success
    
    def _calculate_performance_metrics(self, agent: BaseAgent) -> Dict[str, float]:
        """Calculate detailed performance metrics for an agent."""
        task_manager = agent.get_component("task_manager")
        
        if not task_manager:
            return {"performance_score": 0.0, "efficiency": 0.0, "task_completion_rate": 0.0}
        
        # Calculate performance based on completed tasks vs difficulty
        completed_tasks = [task for task in task_manager.task_queue if task.status.value == "completed"]
        total_difficulty = sum(task.difficulty for task in task_manager.task_queue) if task_manager.task_queue else 1
        completed_difficulty = sum(task.difficulty for task in completed_tasks)
        
        task_completion_rate = len(completed_tasks) / max(len(task_manager.task_queue), 1)
        difficulty_completion_rate = completed_difficulty / total_difficulty
        
        # Factor in work efficiency
        work_efficiency = getattr(agent, 'work_efficiency', 1.0)
        
        # Calculate overall performance score
        performance_score = (difficulty_completion_rate * 0.6 + 
                           task_completion_rate * 0.3 + 
                           (work_efficiency - 1.0) * 0.1)  # work_efficiency around 1.0 is normal
        
        return {
            "performance_score": max(0.0, min(1.0, performance_score)),
            "efficiency": work_efficiency,
            "task_completion_rate": task_completion_rate,
            "difficulty_completion_rate": difficulty_completion_rate
        }
    
    def _calculate_simple_performance(self, agent: BaseAgent) -> Dict[str, float]:
        """Calculate simple performance metrics for casual check-ins."""
        task_manager = agent.get_component("task_manager")
        
        if not task_manager or not task_manager.current_task:
            return {"performance_score": 0.5}  # Neutral if no current task
        
        # Simple metric: current task progress vs difficulty
        current_task = task_manager.current_task
        progress = current_task.get_progress()
        difficulty_factor = min(current_task.difficulty / 10.0, 1.0)  # Normalize difficulty
        
        # Higher progress relative to difficulty = better performance
        performance_score = progress / max(difficulty_factor, 0.1)
        
        return {
            "performance_score": max(0.0, min(1.0, performance_score))
        }
    
    def _update_team_efficacy_perception(self, observer: BaseAgent, observed_performance: Dict[str, float], weight: float = 1.0) -> bool:
        """Update an agent's perception of team efficacy based on observing another's performance."""
        if not hasattr(observer, 'perceived_team_efficacy'):
            observer.perceived_team_efficacy = 0.5  # Initialize to neutral
        
        observed_score = observed_performance.get("performance_score", 0.5)
        
        # Update perception with weighted moving average
        learning_rate = 0.1 * weight  # How much this observation affects perception
        observer.perceived_team_efficacy = (
            (1 - learning_rate) * observer.perceived_team_efficacy + 
            learning_rate * observed_score
        )
        
        # Ensure bounds
        observer.perceived_team_efficacy = max(0.0, min(1.0, observer.perceived_team_efficacy))
        
        observer.log_action("team_efficacy_updated", {
            "new_perception": observer.perceived_team_efficacy,
            "observed_performance": observed_score,
            "weight": weight
        })
        
        return True
