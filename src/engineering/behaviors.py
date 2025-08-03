"""
Engineering-specific behaviors that can be attached to agents.
"""

import random
import math
from typing import TYPE_CHECKING
from ..framework.interfaces import AgentBehavior

if TYPE_CHECKING:
    from ..framework.core.agent import BaseAgent
    from ..framework.core.model import BaseModel

class WorkBehavior(AgentBehavior):
    """Behavior for working on assigned tasks."""
    
    def can_execute(self, agent: 'BaseAgent', model: 'BaseModel') -> bool:
        """Check if agent can work (has tasks and is available)."""
        return (hasattr(agent, 'is_available') and agent.is_available and
                hasattr(agent, 'current_task') and agent.current_task is not None)
    
    def execute(self, agent: 'BaseAgent', model: 'BaseModel') -> None:
        """Execute work on current task."""
        task_manager = agent.get_component("task_manager")
        if task_manager and not task_manager.all_tasks_completed:
            # Work is handled in the task_manager component step
            pass

class LearnBehavior(AgentBehavior):
    """Behavior for learning required knowledge."""
    
    def can_execute(self, agent: 'BaseAgent', model: 'BaseModel') -> bool:
        """Check if agent needs to learn something."""
        task_manager = agent.get_component("task_manager")
        knowledge_manager = agent.get_component("knowledge_manager")
        
        if not task_manager or not knowledge_manager or not task_manager.current_subtask:
            return False
        
        return not knowledge_manager.has_all_required_knowledge(
            task_manager.current_subtask.required_knowledge
        )
    
    def execute(self, agent: 'BaseAgent', model: 'BaseModel') -> None:
        """Execute learning behavior."""
        task_manager = agent.get_component("task_manager")
        knowledge_manager = agent.get_component("knowledge_manager")
        communication_manager = agent.get_component("communication_manager")
        
        if not all([task_manager, knowledge_manager, communication_manager]):
            return
        
        missing_knowledge = knowledge_manager.get_missing_knowledge(
            task_manager.current_subtask.required_knowledge
        )
        
        if missing_knowledge:
            communication_manager.seeking_knowledge = True
            
            # Try to learn each missing concept
            for concept in missing_knowledge:
                # Check if we know agents with this knowledge
                agents_with_knowledge = knowledge_manager.find_agents_with_knowledge(concept)
                if agents_with_knowledge:
                    communication_manager.searching_agents = True
                    communication_manager.searching_agents_targets = agents_with_knowledge
                
                # Continue learning the concept
                knowledge_manager.learn_concept(concept)

class CollaborationBehavior(AgentBehavior):
    """Behavior for collaborating with other agents."""
    
    def can_execute(self, agent: 'BaseAgent', model: 'BaseModel') -> bool:
        """Check if agent can collaborate."""
        return (hasattr(agent, 'motivation') and agent.motivation > 0.5 and
                hasattr(agent, 'communication_skill') and agent.communication_skill > 0.3)
    
    def execute(self, agent: 'BaseAgent', model: 'BaseModel') -> None:
        """Execute collaboration behavior."""
        # Collaboration happens through interactions initiated by CommunicationManager
        pass

class MovementBehavior(AgentBehavior):
    """Behavior for agent movement in space."""
    
    def can_execute(self, agent: 'BaseAgent', model: 'BaseModel') -> bool:
        """Check if agent can move."""
        return hasattr(model, 'space') and agent.position is not None
    
    def execute(self, agent: 'BaseAgent', model: 'BaseModel') -> None:
        """Execute movement behavior."""
        communication_manager = agent.get_component("communication_manager")

        previous_position = agent.position
        
        # Move toward target agents if searching
        if (communication_manager and communication_manager.searching_agents 
            and communication_manager.searching_agents_targets):
            target_agent = self._get_closest_target_agent(agent, model, 
                                                        communication_manager.searching_agents_targets)
            if target_agent and not self._move_toward_agent(agent, model, target_agent):
                self._take_random_step(agent, model)
        else:
            self._take_random_step(agent, model)

        # agent.log_action("moved", {
        #     "from": previous_position,
        #     "to": agent.position,
        #     "step": model.step_count
        # })
    
    def _get_closest_target_agent(self, agent, model, target_ids):
        """Get the closest target agent."""
        min_distance = float('inf')
        closest_agent = None
        
        for target_id in target_ids:
            target_agent = model.get_agent_by_id(int(target_id))
            if target_agent and hasattr(target_agent, 'position') and target_agent.position:
                distance = self._calculate_distance(agent.position, target_agent.position)
                if distance < min_distance:
                    min_distance = distance
                    closest_agent = target_agent
        
        return closest_agent
    
    def _calculate_distance(self, pos1, pos2):
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _move_toward_agent(self, agent, model, target_agent):
        """Move toward a target agent."""
        if not target_agent.position:
            return False
        
        possible_steps = model.space.get_neighborhood(
            agent.position, moore=True, include_center=False
        )
        
        best_move = None
        best_distance = float('inf')
        
        for step in possible_steps:
            distance = math.sqrt(
                (step[0] - target_agent.position[0])**2 + 
                (step[1] - target_agent.position[1])**2
            )
            if distance < best_distance:
                best_distance = distance
                best_move = step
        
        if best_move:
            model.space.move_agent(agent, best_move)
            agent.position = best_move
            return True
        
        return False
    
    def _take_random_step(self, agent, model):
        """Take a random step."""
        possible_steps = model.space.get_neighborhood(
            agent.position, moore=True, include_center=False
        )
        if possible_steps:
            new_position = model.random.choice(possible_steps)
            model.space.move_agent(agent, new_position)
            agent.position = new_position


class EvaluationBehavior(AgentBehavior):
    """Behavior for agents to evaluate team members' performance."""
    
    def __init__(self, evaluation_frequency: float = 0.05):
        """
        Initialize evaluation behavior.
        
        Args:
            evaluation_frequency: Probability of performance evaluation per step (default 5%)
        """
        self.evaluation_frequency = evaluation_frequency
    
    def can_execute(self, agent: 'BaseAgent', model: 'BaseModel') -> bool:
        """Check if agent can conduct evaluations."""
        # Agent should have reasonable communication skills and motivation
        return (hasattr(agent, 'communication_skill') and agent.communication_skill > 0.2 and
                hasattr(agent, 'motivation') and agent.motivation > 0.3 and
                hasattr(model, 'space') and agent.position is not None)
    
    def execute(self, agent: 'BaseAgent', model: 'BaseModel') -> None:
        """Execute evaluation behavior."""
        # Get nearby agents
        if not hasattr(model, 'space'):
            return
            
        neighbors = model.space.get_neighbors(
            agent.position, moore=True, include_center=False, radius=2
        )
        
        if not neighbors:
            return
        
        rand = random.random()
        interaction_type = None
        
        if rand < self.evaluation_frequency:
            interaction_type = "performance_evaluation"
        
        if interaction_type:
            # Choose a random neighbor to evaluate
            target_agent = random.choice(neighbors)
            
            if hasattr(target_agent, 'communication_skill'):
                success = agent.interact_with(target_agent, interaction_type)
                
                if success:
                    agent.log_action(f"{interaction_type}_initiated", {
                        "target_agent": target_agent.unique_id,
                        "step": model.step_count
                    })

