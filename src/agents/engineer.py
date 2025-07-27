from typing import List, Optional, Dict, Any, TYPE_CHECKING # NEW: Import TYPE_CHECKING
from ..types import *
from .base import BaseAgent
from .components.communicator import Communicator, InteractionRecord
from .components.task_tracker import TaskTracker, TaskStatus, SubTaskStatus
from .components.knowledge_manager import KnowledgeManager
from .components.knowledge_network import KnowledgeNetwork
import random
import math

if TYPE_CHECKING:
    from ..model import EngineeringTeamModel

class EngineerAgent(BaseAgent, Communicator):
    """Represents an individual engineer."""
    
    def __init__(self, unique_id: int, model: 'EngineeringTeamModel'):
        """Initialize an EngineerAgent."""
        super().__init__(model)
        self.knowledge_manager = KnowledgeManager(self)
        self.knowledge_network = KnowledgeNetwork()
        self.interaction_handler = Communicator(self)
        self.task_tracker = TaskTracker(self)
        
        # Psychological Safety
        self.pps: float = random.uniform(0.0, 1.0) # perceived psychological safety
        self.cps: float = random.uniform(-1.0, 1.0) # contributed psychological safety

        self.learning_rate: float = random.uniform(0.01, 0.1)  # Rate at which knowledge increases
        self.communication_skill: float = random.uniform(0.1, 1.0)  # Communication skill (0.1 to 1.0)
        self.motivation: float = random.uniform(0.1, 1.0)  # Motivation level (0.5 to 1.0)        
        self.availability: float = random.uniform(0.5, 1.0)  # Availability for tasks (0.5 to 1.0)

        # Interaction tracking
        self.interaction_history: List[InteractionRecord] = []
        self.help_requests_made: int = 0
        self.help_requests_received: int = 0

        # Work tracking
        self.work_efficiency: float = random.uniform(0.5, 1.5)  # Multiplier for work progress
        self.focus_time: int = 0  # Time spent on current task without interruption
    
        self.seeking_knowledge: bool = False  # Whether the engineer is actively seeking knowledge
        self.seeking_agent: bool = False
        self.seeking_agent_targets: List[EngineerAgent] = []        

    def step(self):
        """Engineer step behavior."""
        if not self.task_tracker.all_tasks_completed:
            self.task_tracker.work_on_task()
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
            elif self.task_tracker.current_subtask:
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
                "current_task": self.task_tracker.current_task.id if self.task_tracker.current_task else None,
                "task_progress": self.task_tracker.current_task.get_progress() if self.task_tracker.current_task else None,
                "current_subtask": self.task_tracker.current_subtask.id if self.task_tracker.current_subtask else None,
                "subtask_progress": self.task_tracker.current_subtask.progress if self.task_tracker.current_subtask else None,
            })

    
    def handle_collaboration(self, initiating_agent: 'EngineerAgent', details: Dict[str, Any]):
        initiating_agent.receive_shared_knowledge(self.agent.unique_id, random.choice(self.agent.learned_knowledge))
        self.receive_shared_knowledge(initiating_agent.unique_id, random.choice(initiating_agent.learned_knowledge))

    def handle_knowledge_request(self, initiating_agent: 'EngineerAgent', details: Dict[str, Any]):
        if 'requested_knowledge' not in details:
            return
        
        if self.agent.get_shareable_knowledge(details['requested_knowledge']):
            self.initiate_interaction(initiating_agent, 'knowledge_share', details={'shared_knowledge': random.choice(self.agent.get_shareable_knowledge(details['requested_knowledge']))})
        

    def handle_knowledge_share(self, initiating_agent: 'EngineerAgent', details: Dict[str, Any]):
        if 'shared_knowledge' not in details:
            return
        
        self.agent.receive_shared_knowledge(initiating_agent.unique_id, details['shared_knowledge'])
        self.agent.add_agent_knowledge(initiating_agent.unique_id, details["shared_knowledge"])

    def handle_help_request(self, initiating_agent: 'EngineerAgent', details: Dict[str, Any]):
        pass

    def handle_help_offer(self, initiating_agent: 'EngineerAgent', details: Dict[str, Any]):
        pass

    def handle_feedback(self, initiating_agent: 'EngineerAgent', details: Dict[str, Any]):
        pass


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
                dx = abs(step[0] - target.pos[0])
                dy = abs(step[1] - target.pos[1])
                distance = math.sqrt(dx**2 + dy**2)
                if distance < best_distance:
                    best_distance = distance
                    best_move = step
            
            if best_move:
                self.model.grid.move_agent(self, best_move)
                return True
        
        return False
    
    def initiate_interaction(self, recipient_agent, interaction_type, details = None):
        super().initiate_interaction(recipient_agent, interaction_type, details)
        return self.interaction_handler.initiate_interaction(recipient_agent, interaction_type, details)

    def receive_interaction(self, initiating_agent, interaction_type, details = None):
        super().receive_interaction(initiating_agent, interaction_type, details)
        return self.interaction_handler.receive_interaction(initiating_agent, interaction_type, details)
    
    def __getattr__(self, name):
        # Try _b first, then _c
        for obj in [self.interaction_handler, self.knowledge_manager, self.knowledge_network, self.task_tracker]:
            try:
                return getattr(obj, name)
            except AttributeError:
                continue
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")