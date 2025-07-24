from typing import List, Optional, Dict, Any, TYPE_CHECKING # NEW: Import TYPE_CHECKING
from ..types import *
from .base import BaseAgent
from .components.interaction_handler import InteractionHandler, InteractionRecord
from .components.task_tracker import TaskTracker, TaskStatus, SubTaskStatus
from .components.knowledge_manager import KnowledgeManager
from .components.knowledge_network import KnowledgeNetwork
import random
import math

if TYPE_CHECKING:
    from ..model import EngineeringTeamModel

class EngineerAgent(BaseAgent):
    """Represents an individual engineer."""
    
    def __init__(self, unique_id: int, model: 'EngineeringTeamModel'):
        """Initialize an EngineerAgent."""
        super().__init__(model)
        self.knowledge_manager = KnowledgeManager(self)
        self.knowledge_network = KnowledgeNetwork()
        self.interaction_handler = InteractionHandler(self)
        self.task_tracker = TaskTracker(self)
        
        # Psychological Safety
        self.pps: float = random.uniform(0.0, 1.0) # perceived psychological safety
        self.cps: float = random.uniform(-1.0, 1.0) # contributed psychological safety

        self.learning_rate: float = random.uniform(0.01, 0.1)  # Rate at which knowledge increases
        self.communication_skill: float = random.uniform(0.1, 1.0)  # Communication skill (0.1 to 1.0)
        self.motivation: float = random.uniform(0.1, 1.0)  # Motivation level (0.5 to 1.0)        
        self.availability: float = random.uniform(0.5, 1.0)  # Availability for tasks (0.5 to 1.0)

        # Knowledge system
        self.learned_knowledge: set[str] = {}  # Concepts the engineer knows
        self.knowledge_network: Dict[int, set[str]] = {}  # { unique_id : {"K001", "K002", ...}, }
        self.concept_learning_progress: Dict[str, float] = {} # {concept_id: progress (0-1)}

        # Interaction tracking
        self.interaction_history: List[InteractionRecord] = []
        self.help_requests_made: int = 0
        self.help_requests_received: int = 0

        # Work tracking
        self.work_efficiency: float = random.uniform(0.5, 1.5)  # Multiplier for work progress
        self.focus_time: int = 0  # Time spent on current task without interruption
    
        self.seeking_knowledge: bool = False  # Whether the engineer is actively seeking knowledge
        self.seeking_agent = False
        self.seeking_agent_targets: List[EngineerAgent] = []

        
    def work_on_task(self):
        """Progress on current task."""
       
        if not self.current_task:
            self.current_task = next((task for task in self.assigned_tasks if task.status == TaskStatus.BACKLOG), None)
            if not self.current_task:
                print(f"Engineer {self.unique_id} has no tasks assigned.")
                return
            else:
                self.current_task.start()
                print(f"Engineer {self.unique_id} started working on task {self.current_task.id}.")
        if self.current_task.status == TaskStatus.IN_PROGRESS:
            if self.current_subtask:
                print(f"Engineer {self.unique_id} is working on subtask {self.current_subtask.id} of task {self.current_task.id}.")
                self.work_on_subtask()
                if all(subtask.status == SubTaskStatus.COMPLETED for subtask in self.current_task.subtasks):
                    # All subtasks completed, mark task as completed
                    self.current_task.complete()
                    self.completed_tasks.append(self.current_task.id)
                    self._log_history("task_completed", {"task_id": self.current_task.id})
                    self.current_task = None
                    self.current_subtask = None
                    if all(task.status == TaskStatus.COMPLETED for task in self.assigned_tasks):
                        self.all_tasks_completed = True
                        self._log_history("all_tasks_completed", {"engineer_id": self.unique_id})
                elif self.current_subtask.is_complete():
                    # Move to the next subtask if current one is completed
                    self.current_subtask = next((subtask for subtask in self.current_task.subtasks if subtask.status == SubTaskStatus.ACTIVE), None)
            else:
                # If no current subtask, start the first subtask
                self.current_subtask = next((subtask for subtask in self.current_task.subtasks if subtask.status == SubTaskStatus.NOT_STARTED), None)
            
    
    def work_on_subtask(self):
        """Progress on current subtask."""
        if not self.current_subtask:
            return
        
        self._log_history("work_on_subtask", {"subtask_id": self.current_subtask.id})
        
        if all(required_knowledge in self.learned_knowledge for required_knowledge in self.current_subtask.required_knowledge):
            # If all required knowledge is known, work on the subtask
            progress_increment = self.work_efficiency * 0.1
            self.current_subtask.progress += progress_increment
            
            if self.current_subtask.progress >= 1.0:
                # Subtask completed
                self.current_subtask.complete()
                self.completed_subtasks.append(self.current_subtask.id)
                self._log_history("subtask_completed", {"subtask_id": self.current_subtask.id})
                self.seeking_agent_targets = []
                self.seeking_knowledge = False
                self.seeking_agent = False
        else:
            # If not all required knowledge is known, try to learn
            missing_knowledge = self.get_missing_knowledge()
            if not missing_knowledge:
                print(f"Engineer {self.unique_id} has no missing knowledge for subtask {self.current_subtask.id}.")
            
            self.seeking_knowledge = True
            for concept in missing_knowledge:
                if self.knows_agent_with_knowledge(concept):
                    self.seeking_agent = True
                    self.seeking_agent_targets = self.find_agents_with_needed_knowledge()

                if concept not in self.concept_learning_progress:
                    self.concept_learning_progress[concept] = 0.0
                
                self.concept_learning_progress[concept] += self.learning_rate * self.work_efficiency * random.uniform(0.5,1.5)
                
                if self.concept_learning_progress[concept] >= 1.0:
                    # Concept learned
                    self.learned_knowledge.add(concept)
                    self._log_history("knowledge_learned", {"concept": concept})
                    del self.concept_learning_progress[concept]
        

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
                    self.log_interaction(recipient, interaction_type="help_request")
            elif self.seeking_knowledge:
                recipient = self.random.choice(neighbors)
                if isinstance(recipient, EngineerAgent):
                    self.initiate_interaction(recipient, interaction_type="knowledge_request")
            elif self.task_tracker.current_subtask:
                recipient = self.random.choice(neighbors)
                if isinstance(recipient, EngineerAgent):
                    self.log_interaction(recipient, interaction_type="collaboration")
        elif self.seeking_agent and self.seeking_agent_targets:
            # If seeking agent is enabled, try to move toward a target
            target = self.get_closest_agent(self.seeking_agent_targets) if self.current_subtask else None
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

    def take_random_step(self):
        """Take a random step in the grid."""
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=True)
        if possible_steps:
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    
    def knows_agent_has_knowledge(self, unique_id: int, concept: str) -> bool:
        """Check if we know that a specific agent has a specific knowledge concept."""
        return (unique_id in self.knowledge_network and 
                concept in self.knowledge_network[unique_id])

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
        
        for unique_id in agents_with_knowledge:
            target_agent = self.model.get_agent_by_id(unique_id)
            if target_agent and target_agent.pos:
                distance = self.model.grid.get_distance(self.pos, target_agent.pos)
                if distance < min_distance:
                    min_distance = distance
                    nearest_agent = target_agent
        
        return nearest_agent
    
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

    def receive_interaction(self, sender_agent, interaction_type, details = None):
        super().receive_interaction(sender_agent, interaction_type, details)
        return self.interaction_handler.receive_interaction(sender_agent, interaction_type, details)
    
    def __getattr__(self, name):
        # Try _b first, then _c
        for obj in [self.interaction_handler, self.knowledge_manager, self.knowledge_network, self.task_tracker]:
            try:
                return getattr(obj, name)
            except AttributeError:
                continue
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")