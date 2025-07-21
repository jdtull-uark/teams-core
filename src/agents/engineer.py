from typing import List, Optional, Dict, Any, TYPE_CHECKING # NEW: Import TYPE_CHECKING
from ..types import *
from .base import BaseAgent
from .components.interaction_handler import Interaction, InteractionRecord
from .components.tasking import Tasking, TaskStatus, SubTaskStatus
from .components.knowledge_manager import KnowledgeManager
from .components.knowledge_network import KnowledgeNetwork
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
        self.knowledge_network = KnowledgeNetwork()
        self.interaction = Interaction(self)
        self.tasking = Tasking(self)
        
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
    
        self.searching_agents = False
        self.searching_agents_targets: List[EngineerAgent] = []


    def step(self):
        """Engineer step behavior."""
        if not self.tasking.all_tasks_completed:
            self.tasking.work_on_task()
        else:
            self._log_history("all_tasks_completed", {"engineer_id": self.unique_id})

        # Attempt to interact with a nearby agent
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        if neighbors:
            if any(agent in neighbors for agent in self.searching_agents_targets):
                recipient = [agent for agent in neighbors if agent in self.searching_agents_targets][0]
                if isinstance(recipient, EngineerAgent):
                    self.initiate_interaction(recipient, interaction_type="help_request")
            elif self.seeking_knowledge:
                recipient = self.random.choice(neighbors)
                if isinstance(recipient, EngineerAgent):
                    self.initiate_interaction(recipient, interaction_type="knowledge_request")
            elif self.tasking.current_subtask:
                recipient = self.random.choice(neighbors)
                if isinstance(recipient, EngineerAgent):
                    self.initiate_interaction(recipient, interaction_type="collaboration")
        elif self.searching_agents and self.searching_agents_targets:
            target = self.get_closest_agent(self.searching_agents_targets) if self.current_subtask else None
            if target:
                if not self.move_toward_agent(target):
                    # If we can't move toward the target, just take a random step
                    self.take_random_step()
                    return
                
        self.take_random_step()

        if self.model.steps % 10 == 0:
            # Log current state every 10 steps
            self._log_history("check-in", {
                "step": self.model.steps,
                "current_task": self.tasking.current_task.id if self.tasking.current_task else None,
                "task_progress": self.tasking.current_task.get_progress() if self.tasking.current_task else None,
                "current_subtask": self.tasking.current_subtask.id if self.tasking.current_subtask else None,
                "subtask_progress": self.tasking.current_subtask.progress if self.tasking.current_subtask else None,
            })

    def take_random_step(self):
        """Take a random step in the grid."""
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        if possible_steps:
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    def get_closest_agent(self, targets: List['EngineerAgent']) -> Optional['EngineerAgent']:
        """Get the closest agent who has a specific knowledge concept."""
        if not targets:
            return None
        
        nearest_agent = None
        min_distance = float('inf')
        
        for unique_id in targets:
            target_agent = self.model.get_agent_by_id(unique_id)
            if target_agent and target_agent.pos:
                # Calculate Manhattan or Euclidean distance
                dx = abs(self.pos[0] - target_agent.pos[0])
                dy = abs(self.pos[1] - target_agent.pos[1])
                distance = dx + dy  # Manhattan distance
                # Or use: distance = math.sqrt(dx**2 + dy**2)  # Euclidean distance
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_agent = target_agent
        
        return nearest_agent

    
    def move_toward_agent(self, target: Optional['EngineerAgent']) -> bool:
        """Move toward the nearest agent in seeking_agent_targets."""
        if target:
            # Get possible moves
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
            
            # Find the move that gets us closest to the target
            best_move = None
            best_distance = float('inf')
            
            for step in possible_steps:
                dx = abs(self.pos[0] - target.pos[0])
                dy = abs(self.pos[1] - target.pos[1])
                distance = math.sqrt(dx**2 + dy**2)
                if distance < best_distance:
                    best_distance = distance
                    best_move = step
            
            if best_move:
                self.model.grid.move_agent(self, best_move)
                return True
        
        return False