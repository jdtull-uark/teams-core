from typing import List, Optional, Dict, Any, TYPE_CHECKING # NEW: Import TYPE_CHECKING
from ..types import Task, TaskStatus, InteractionType
from .base import BaseAgent
import random
import math

if TYPE_CHECKING:
    from ..model import EngineeringTeamModel

class EngineerAgent(BaseAgent):
    """Represents an individual engineer."""
    
    def __init__(self, unique_id: int, model: 'EngineeringTeamModel'):
        super().__init__(unique_id, model)
        
        self.current_task: Optional[Task] = None
        self.completed_tasks: List[str] = []
        
        self.pps: float = random.uniform(0.0, 1.0)
        self.cps: float = random.uniform(-1.0, 1.0)
        self.knowledge: float = random.uniform(0.0, 1)

        
    def work_on_task(self):
        """Progress on current task."""
        if not self.current_task:
            return
            
        # TODO: Implement task progress logic
        if hasattr(self, '_work_counter'):
            self._work_counter += 1
        else:
            self._work_counter = 1
            
        if self._work_counter >= 5:  # Simple completion after 5 steps
            self.current_task.status = TaskStatus.COMPLETED
            self.completed_tasks.append(self.current_task.id)
            self.current_task = None
            self._work_counter = 0
    
    def step(self):
        """Engineer step behavior."""
        if self.current_task:
            self.work_on_task()
        
        # Attempt to interact with a nearby agent
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        if neighbors:
            recipient = self.random.choice(neighbors)
            if isinstance(recipient, EngineerAgent):
                interaction_details = {
                    "interaction_duration": self.random.uniform(1.0, 5.0),
                    "sender_speaking_percentage": self.random.uniform(0.05, 0.95)
                }
                self.initiate_interaction(recipient, interaction_type="collaboration", details=interaction_details)

        
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)


    def process_interaction(self, other_agent: 'EngineerAgent', interaction_type: Any = None, speaking_percentage: int = 0,  details: Dict[str, Any] = None):
        if self.knowledge < other_agent.knowledge:
            self.knowledge += 0.05 * details.get("interaction_duration", 0)

        speaking_time = speaking_percentage * details["interaction_duration"]
        
        self.pps += other_agent.cps * speaking_time * 0.01

        self.update_cps()

    def receive_interaction(self, sender_agent: 'EngineerAgent', interaction_type: Any = None, details: Dict[str, Any] = None):
        super().receive_interaction(sender_agent, interaction_type, details)

        self.process_interaction(sender_agent, speaking_percentage = 1 - details["sender_speaking_percentage"], details = details)


    def initiate_interaction(self, recipient_agent, interaction_type: Any, details: Dict[str, Any] = None):
        super().initiate_interaction(recipient_agent, interaction_type, details)

        self.process_interaction(recipient_agent, speaking_percentage = details["sender_speaking_percentage"], details = details)
    
    def update_cps(self):
        # Normalize PPS from [0, 1] to [-1, 1]
        target_cps = 2 * self.pps - 1

        # Move CPS toward the normalized PPS
        self.cps += 0.05 * (target_cps - self.cps)

        # Clamp CPS to [-1, 1]
        self.cps = max(min(self.cps, 1.0), -1.0)
