# src/agents/engineer.py
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from ..types import *
from .base import BaseAgent
from .components.communicator import Communicator, InteractionRecord
from .components.task_handler import TaskHandler, TaskStatus, SubTaskStatus
from .components.knowledge_manager import KnowledgeManager
import random
import math

if TYPE_CHECKING:
    from ..model import EngineeringTeamModel

class EngineerAgent(BaseAgent, TaskHandler, Communicator, KnowledgeManager):
    """Represents an individual engineer."""
    
    def __init__(self, model: 'EngineeringTeamModel'):
        """Initialize an EngineerAgent."""
        BaseAgent.__init__(self, model)
        TaskHandler.__init__(self)
        Communicator.__init__(self)
        KnowledgeManager.__init__(self)
        
        # Psychological Safety
        self.pps: float = random.uniform(0.0, 1.0) # perceived psychological safety
        self.cps: float = random.uniform(-1.0, 1.0) # contributed psychological safety

        self.learning_rate: float = random.uniform(0.01, 0.1)  # Rate at which knowledge increases
        self.communication_skill: float = random.uniform(0.1, 1.0)  # Communication skill (0.1 to 1.0)
        self.motivation: float = random.uniform(0.1, 1.0)  # Motivation level (0.5 to 1.0)        
        self.is_available: bool = False  # Availability for tasks (0.5 to 1.0)

        # Work tracking
        self.work_efficiency: float = random.uniform(0.5, 1.5)  # Multiplier for work progress
        self.focus_time: int = 0  # Time spent on current task without interruption
    
        self.seeking_knowledge: bool = False  # Whether the engineer is actively seeking knowledge
        self.searching_agents: bool = False
        self.searching_agents_targets: List[str] = []  # Changed to List[str] for agent IDs

    def step(self):
        """Engineer step behavior."""
        if not self.all_tasks_completed:
            self.work_on_task()
        else:
            self._log_history("all_tasks_completed", {"engineer_id": self.unique_id})

        # Attempt to interact with a nearby agent
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        if neighbors:
            recipient = None
            interaction_type = None

            if self.searching_agents and any(str(agent.unique_id) in self.searching_agents_targets for agent in neighbors):
                recipient = next((agent for agent in neighbors if str(agent.unique_id) in self.searching_agents_targets), None)
                interaction_type = "help_request"
            elif self.seeking_knowledge:
                recipient = self.random.choice(neighbors)
                interaction_type = "knowledge_request"
            elif self.current_subtask:
                recipient = self.random.choice(neighbors)
                interaction_type = "collaboration"
            
            if recipient and isinstance(recipient, EngineerAgent):
                details = {"interaction_type": interaction_type}
                self.initiate_interaction(recipient, interaction_type, details)

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
                "current_task": self.current_task.id if self.current_task else None,
                "task_progress": self.current_task.get_progress() if self.current_task else None,
                "current_subtask": self.current_subtask.id if self.current_subtask else None,
                "subtask_progress": self.current_subtask.progress if self.current_subtask else None,
            })

    def initiate_interaction(self, recipient_agent, interaction_type, details=None):        
        if not details:
            details = {}
            
        details.update({
            "initiating_agent": self,
            "recipient_agent": recipient_agent,
            "interaction_type": interaction_type,
            "interaction_duration": random.uniform(0.5, 10)
        })
        
        self.log_interaction(status='sent', details=details)
        super().initiate_interaction(recipient_agent, interaction_type, details)

    def receive_interaction(self, initiating_agent, interaction_type, details=None):
        if not details:
            return

        self.log_interaction(status='received', details=details)
        self.process_interaction(initiating_agent=initiating_agent, interaction_type=interaction_type, details=details)

    def process_interaction(self, initiating_agent: 'BaseAgent', interaction_type, details=None):
        match interaction_type:
            case 'collaboration':
                self.handle_collaboration(initiating_agent=initiating_agent, details=details)
            case 'knowledge_request':
                self.handle_knowledge_request(initiating_agent=initiating_agent, details=details)
            case 'knowledge_share':
                self.handle_knowledge_share(initiating_agent=initiating_agent, details=details)
            case 'help_request':
                self.handle_help_request(initiating_agent=initiating_agent, details=details)
            case 'help_offer':
                self.handle_help_offer(initiating_agent=initiating_agent, details=details)
            case 'feedback':
                self.handle_feedback(initiating_agent=initiating_agent, details=details)
            case _:  # Default case
                print(f'Unknown interaction type encountered for type {type(self).__name__}')

    def handle_collaboration(self, initiating_agent: 'EngineerAgent', details: Dict[str, Any]):
        # Share random knowledge with each other
        if self.learned_knowledge:
            shared_concept = random.choice(list(self.learned_knowledge))
            initiating_agent.receive_shared_knowledge(str(self.unique_id), shared_concept)
        
        if initiating_agent.learned_knowledge:
            received_concept = random.choice(list(initiating_agent.learned_knowledge))
            self.receive_shared_knowledge(str(initiating_agent.unique_id), received_concept)

    def handle_knowledge_request(self, initiating_agent: 'EngineerAgent', details: Dict[str, Any]):
        # Determine what knowledge is being requested
        if self.current_subtask:
            requested_knowledge = self.get_missing_knowledge()
        else:
            requested_knowledge = []
        
        if requested_knowledge:
            shareable = self.get_shareable_knowledge(requested_knowledge)
            if shareable:
                shared_concept = random.choice(shareable)
                self.initiate_interaction(
                    initiating_agent, 
                    'knowledge_share', 
                    {'shared_knowledge': shared_concept}
                )
            elif self.knows_any_agent_with_knowledge(requested_knowledge[0]):
                agents_with_knowledge = self.get_agents_with_knowledge(requested_knowledge[0])
                self.initiate_interaction(
                    initiating_agent, 
                    'knowledge_share', 
                    {'shared_network': agents_with_knowledge}
                )

    def handle_knowledge_share(self, initiating_agent: 'EngineerAgent', details: Dict[str, Any]):
        if 'shared_knowledge' in details:
            concept = details['shared_knowledge']
            self.receive_shared_knowledge(str(initiating_agent.unique_id), concept)
        elif 'shared_network' in details:
            agents_with_knowledge = details['shared_network']
            # Add these agents to our knowledge network
            for agent_id in agents_with_knowledge:
                # We don't know what specific knowledge they have, so we'll learn it through interaction
                pass

    def handle_help_request(self, initiating_agent: 'EngineerAgent', details: Dict[str, Any]):
        if self.is_available and self.motivation >= 0.7:
            self.log_interaction(status='help_request_accepted', details=details)
            # Could implement help_agent method or just log acceptance
        else:
            self.log_interaction(status='help_request_denied', details=details)

    def handle_help_offer(self, initiating_agent: 'EngineerAgent', details: Dict[str, Any]):
        # Accept help if we need it
        if self.seeking_knowledge or (self.current_subtask and not self.has_all_required_knowledge()):
            self.log_interaction(status='help_offer_accepted', details=details)
        else:
            self.log_interaction(status='help_offer_declined', details=details)

    def handle_feedback(self, initiating_agent: 'EngineerAgent', details: Dict[str, Any]):
        # Process feedback (could affect motivation, psychological safety, etc.)
        self.log_interaction(status='feedback_received', details=details)

    def attempt_learning(self):
        """Attempt to learn missing knowledge for current subtask."""
        if not self.current_subtask:
            return
        
        missing_knowledge = self.get_missing_knowledge(self.current_subtask.required_knowledge)
        if not missing_knowledge:
            return
        
        self.seeking_knowledge = True
        
        # Try to learn each missing concept
        for concept in missing_knowledge:
            if self.knows_any_agent_with_knowledge(concept):
                self.searching_agents = True
                self.searching_agents_targets = self.find_agents_with_needed_knowledge()
            
            self.learn_concept(concept)

    def take_random_step(self):
        """Take a random step in the grid."""
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        if possible_steps:
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    def get_closest_agent(self, target_ids: List[str]) -> Optional['EngineerAgent']:
        """Get the closest agent from the list of target agent IDs."""
        if not target_ids:
            return None
        
        nearest_agent = None
        min_distance = float('inf')
        
        for agent_id in target_ids:
            target_agent = self.model.get_agent_by_id(agent_id)
            if target_agent and target_agent.pos:
                # Calculate Manhattan distance
                dx = abs(self.pos[0] - target_agent.pos[0])
                dy = abs(self.pos[1] - target_agent.pos[1])
                distance = dx + dy
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_agent = target_agent
        
        return nearest_agent

    def move_toward_agent(self, target: Optional['EngineerAgent']) -> bool:
        """Move toward the target agent."""
        if not target or not target.pos:
            return False
            
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