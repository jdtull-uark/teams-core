from typing import List, Optional, Dict, Any, TYPE_CHECKING # NEW: Import TYPE_CHECKING
from ..types import *
from .base import BaseAgent
from .components.interaction_handler import InteractionHandler, InteractionRecord
from .components.task_manager import TaskManager, TaskStatus, SubTaskStatus
from .components.knowledge_manager import KnowledgeManager
import random
import math
import uuid

if TYPE_CHECKING:
    from ..model import EngineeringTeamModel

class EngineerAgent(BaseAgent):
    """Represents an individual engineer."""
    
    def __init__(self, model: 'EngineeringTeamModel'):
        """Initialize an EngineerAgent."""
        super().__init__(model)
        self.knowledge_manager = KnowledgeManager(self)
        self.interaction_handler = InteractionHandler(self)
        self.task_manager = TaskManager(self)
        
        # Psychological Safety
        self.pps: float = random.uniform(0.0, 1.0) # perceived psychological safety
        self.cps: float = random.uniform(-1.0, 1.0) # contributed psychological safety

        self.learning_rate: float = random.uniform(0.01, 0.1)  # Rate at which knowledge increases
        self.communication_skill: float = random.uniform(0.1, 1.0)  # Communication skill (0.1 to 1.0)
        self.motivation: float = random.uniform(0.1, 1.0)  # Motivation level (0.5 to 1.0)        
        self.availability: float = random.uniform(0.5, 1.0)  # Availability for tasks (0.5 to 1.0)

        # Work tracking
        self.work_efficiency: float = random.uniform(0.5, 1.5)  # Multiplier for work progress
        self.focus_time: int = 0  # Time spent on current task without interruption
    
        self.seeking_knowledge: bool = False  # Whether the engineer is actively seeking knowledge
        self.seeking_agent = False
        self.seeking_agent_targets: List[EngineerAgent] = []

        

    def step(self):
        """Engineer step behavior."""
        if not self.task_manager.all_tasks_completed:
            self.task_manager.work_on_task()
        else:
            self._log_history("all_tasks_completed", {"engineer_id": self.unique_id})

        # Attempt to interact with a nearby agent
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        if neighbors:
            if any(agent in neighbors for agent in self.seeking_agent_targets):
                recipient = [agent for agent in neighbors if agent in self.seeking_agent_targets][0]
                if isinstance(recipient, EngineerAgent):
                    self.initiate_interaction(recipient, interaction_type="help_request")
            elif self.seeking_knowledge:
                recipient = self.random.choice(neighbors)
                if isinstance(recipient, EngineerAgent):
                    self.initiate_interaction(recipient, interaction_type="knowledge_request")
            elif self.current_subtask:
                recipient = self.random.choice(neighbors)
                if isinstance(recipient, EngineerAgent):
                    self.initiate_interaction(recipient, interaction_type="collaboration")
        elif self.seeking_agent and self.seeking_agent_targets:
            # If seeking agent is enabled, try to move toward a target
            target = self.get_closest_agent(self.seeking_agent_targets) if self.current_subtask else None
            if target:
                if not self.move_toward_agent(target):
                    # If we can't move toward the target, just take a random step
                    self.take_random_step()
                    return
                
        self.take_random_step()



    def take_random_step(self):
        """Take a random step in the grid."""
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        if possible_steps:
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)


    

    
    def knows_agent_has_knowledge(self, agent_id: int, concept: str) -> bool:
        """Check if we know that a specific agent has a specific knowledge concept."""
        return (agent_id in self.knowledge_network and 
                concept in self.knowledge_network[agent_id])

    def knows_agent_with_knowledge(self, concept: str) -> bool:
        """Check if we know any agent has a specific knowledge concept."""
        return any(concept in concepts for concepts in self.knowledge_network.values())
    
    def get_agents_with_knowledge(self, concept: str) -> List[int]:
        """Get list of agent IDs that we know have a specific knowledge concept."""
        return [agent for agent, concepts in self.knowledge_network.items() 
                if concept in concepts]
    
    def find_agents_with_needed_knowledge(self) -> List[int]:
        """Find agents who have knowledge needed for current subtask."""
        if not self.current_subtask:
            return []
        
        potential_targets = []
        needed_knowledge = self.current_subtask.required_knowledge
        
        for concept in needed_knowledge:
            # Only look for knowledge we don't already have
            if concept not in self.learned_knowledge:
                # Find agents we know have this knowledge
                agents_with_knowledge = self.get_agents_with_knowledge(concept)
                potential_targets.extend(agents_with_knowledge)
        
        # Remove duplicates and return
        return list(set(potential_targets))
    
    def get_missing_knowledge(self) -> List[str]:
        """Get a list of knowledge concepts needed for the current subtask."""

        if not self.current_subtask:
            return []
        
        missing_knowledge = []
        needed_knowledge = self.current_subtask.required_knowledge

        for concept in needed_knowledge:
            # Only include concepts we don't already know
            if concept not in self.learned_knowledge:
                missing_knowledge.append(concept)

        return missing_knowledge
    
    def get_closest_agent_with_knowledge(self, concept: str) -> Optional['EngineerAgent']:
        """Get the closest agent who has a specific knowledge concept."""
        agents_with_knowledge = self.get_agents_with_knowledge(concept)
        
        if not agents_with_knowledge:
            return None
        
        nearest_agent = None
        min_distance = float('inf')
        
        for agent_id in agents_with_knowledge:
            target_agent = self.model.get_agent_by_id(agent_id)
            if target_agent and target_agent.pos:
                distance = self.model.grid.get_distance(self.pos, target_agent.pos)
                if distance < min_distance:
                    min_distance = distance
                    nearest_agent = target_agent
        
        return nearest_agent
    
