from typing import List, Optional, Dict, Any, TYPE_CHECKING # NEW: Import TYPE_CHECKING
from ..types import *
from .base import BaseAgent
from ..rules.psychological_safety_rule import PsychologicalSafetyRule
import random
import math

if TYPE_CHECKING:
    from ..model import EngineeringTeamModel

class EngineerAgent(BaseAgent):
    """Represents an individual engineer."""
    
    def __init__(self, unique_id: int, model: 'EngineeringTeamModel'):
        super().__init__(unique_id, model)
        
        # Task management
        self.current_task: Optional[Task] = None
        self.current_subtask: Optional[SubTask] = None
        self.completed_tasks: List[str] = []
        self.completed_subtasks: List[str] = []
        
        # Psychological Safety
        self.pps: float = random.uniform(0.0, 1.0) # perceived psychological safety
        self.cps: float = random.uniform(-1.0, 1.0) # contributed psychological safety

        self.learning_rate: float = random.uniform(0.01, 0.1)  # Rate at which knowledge increases
        self.communication_skill: float = random.uniform(0.1, 1.0)  # Communication skill (0.1 to 1.0)
        self.motivation: float = random.uniform(0.1, 1.0)  # Motivation level (0.5 to 1.0)        
        self.availability: float = random.uniform(0.5, 1.0)  # Availability for tasks (0.5 to 1.0)

        # Knowledge system
        self.knowledge_concepts: List[str] = []  # Concepts the engineer knows
        self.knowledge_network: Dict[int, List[str]] = {}  # { "Agent01" : ["K001", "K002", "K003"], }
        self.concept_learning_progress: Dict[str, float] = {} # {concept_id: progress (0-1)}

        # Interaction tracking
        self.interaction_history: List[InteractionRecord] = []
        self.help_requests_made: int = 0
        self.help_requests_received: int = 0

        # Work tracking
        self.work_efficiency: float = random.uniform(0.5, 1.5)  # Multiplier for work progress
        self.focus_time: int = 0  # Time spent on current task without interruption
    
        self.seeking_agent = False
        self.seeking_agent_targets: List[EngineerAgent] = []

        
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
            if any(agent in neighbors for agent in self.seeking_agent_targets):
                recipient = [agent for agent in neighbors if agent in self.seeking_agent_targets][0]
                if isinstance(recipient, EngineerAgent):
                    interaction_details = {
                        "interaction_duration": self.random.uniform(1.0, 5.0),
                        "sender_speaking_percentage": self.random.uniform(0.05, 0.95)
                    }
                    self.initiate_interaction(recipient, interaction_type="help_request", details=interaction_details)
            else:
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


    def process_interaction(self, other_agent: 'EngineerAgent', interaction_type: Any = None, speaking_percentage: int = 0, details: Dict[str, Any] = None):
        # Handle specific interaction types
        shared_concepts = []
        if interaction_type == InteractionType.COLLABORATION:
            shared_concepts = self.handle_collaboration(other_agent, details)
        elif interaction_type == InteractionType.HELP_REQUEST:
            shared_concepts = self.handle_help_request(other_agent, details)
        elif interaction_type == InteractionType.HELP_OFFER:
            shared_concepts = self.handle_help_offer(other_agent, details)
        elif interaction_type == InteractionType.KNOWLEDGE_SHARE:
            shared_concepts = self.handle_knowledge_share(other_agent, details)
        elif interaction_type == InteractionType.FEEDBACK:
            shared_concepts = self.handle_feedback(other_agent, details)
        
        speaking_time = speaking_percentage * details["interaction_duration"]
        
        self.pps += other_agent.cps * speaking_time * 0.01
        self.update_cps()
        
        # Record the interaction
        interaction_record = InteractionRecord(
            timestamp=self.model.time,
            initiator_id=str(self.unique_id),
            recipient_id=str(other_agent.unique_id),
            interaction_type=interaction_type,
            duration=details.get("interaction_duration", 0),
            knowledge_shared=shared_concepts
        )
        self.interaction_history.append(interaction_record)

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

    def handle_collaboration(self, other_agent: 'EngineerAgent', details: Dict[str, Any]):
        """Handle collaboration interaction - general knowledge sharing."""
        # Share some knowledge concepts
        shared_concepts = random.sample(self.knowledge_concepts, 
                                    min(2, len(self.knowledge_concepts)))
        
        # Update knowledge network with what we learn about the other agent
        for concept in other_agent.knowledge_concepts:
            if other_agent.unique_id not in self.knowledge_network:
                self.knowledge_network[other_agent.unique_id] = []
            if concept not in self.knowledge_network[other_agent.unique_id]:
                self.knowledge_network[other_agent.unique_id].append(concept)
        
        return shared_concepts

    def handle_help_request(self, other_agent: 'EngineerAgent', details: Dict[str, Any]):
        """Handle help request interaction - targeted knowledge sharing."""
        # If we have knowledge the other agent needs, share it
        shared_concepts = []
        
        # Find concepts we know that the other agent doesn't
        helpful_concepts = [concept for concept in self.knowledge_concepts 
                        if concept not in other_agent.knowledge_concepts]
        
        if helpful_concepts:
            # Share up to 3 helpful concepts
            shared_concepts = random.sample(helpful_concepts, 
                                        min(3, len(helpful_concepts)))
            
            # Add shared concepts to other agent's learning progress
            for concept in shared_concepts:
                if concept not in other_agent.concept_learning_progress:
                    other_agent.concept_learning_progress[concept] = 0.2
        
        # Update our knowledge network
        for concept in other_agent.knowledge_concepts:
            if other_agent.unique_id not in self.knowledge_network:
                self.knowledge_network[other_agent.unique_id] = []
            if concept not in self.knowledge_network[other_agent.unique_id]:
                self.knowledge_network[other_agent.unique_id].append(concept)
        
        return shared_concepts

    def handle_help_offer(self, other_agent: 'EngineerAgent', details: Dict[str, Any]):
        """Handle help offer interaction - proactive knowledge sharing."""
        # Offer knowledge that might be useful
        shared_concepts = []
        
        # Look at what we know about their knowledge gaps
        if other_agent.current_task and other_agent.current_subtask:
            needed_knowledge = other_agent.current_subtask.required_knowledge
            helpful_concepts = [concept for concept in self.knowledge_concepts 
                            if concept in needed_knowledge]
            
            if helpful_concepts:
                shared_concepts = helpful_concepts[:2]  # Offer up to 2 relevant concepts
                
                # Add to their learning progress
                for concept in shared_concepts:
                    if concept not in other_agent.concept_learning_progress:
                        other_agent.concept_learning_progress[concept] = 0.3
        
        # Update knowledge network
        for concept in other_agent.knowledge_concepts:
            if other_agent.unique_id not in self.knowledge_network:
                self.knowledge_network[other_agent.unique_id] = []
            if concept not in self.knowledge_network[other_agent.unique_id]:
                self.knowledge_network[other_agent.unique_id].append(concept)
        
        return shared_concepts

    def handle_knowledge_share(self, other_agent: 'EngineerAgent', details: Dict[str, Any]):
        """Handle knowledge sharing interaction - explicit knowledge transfer."""
        # Share random knowledge concepts
        shared_concepts = random.sample(self.knowledge_concepts, 
                                    min(1, len(self.knowledge_concepts)))
        
        # Directly add to other agent's knowledge
        for concept in shared_concepts:
            if concept not in other_agent.knowledge_concepts:
                other_agent.knowledge_concepts.append(concept)
        
        # Update knowledge network
        for concept in other_agent.knowledge_concepts:
            if other_agent.unique_id not in self.knowledge_network:
                self.knowledge_network[other_agent.unique_id] = []
            if concept not in self.knowledge_network[other_agent.unique_id]:
                self.knowledge_network[other_agent.unique_id].append(concept)
        
        return shared_concepts

    def handle_feedback(self, other_agent: 'EngineerAgent', details: Dict[str, Any]):
        """Handle feedback interaction - performance and knowledge feedback."""
        # Provide feedback on work or knowledge
        shared_concepts = []
        
        # If giving feedback, might share related knowledge
        if random.random() < 0.3:  # 30% chance to share knowledge with feedback
            shared_concepts = random.sample(self.knowledge_concepts, 
                                        min(1, len(self.knowledge_concepts)))
            
            for concept in shared_concepts:
                if concept not in other_agent.concept_learning_progress:
                    other_agent.concept_learning_progress[concept] = 0.1
        
        # Update knowledge network
        for concept in other_agent.knowledge_concepts:
            if other_agent.unique_id not in self.knowledge_network:
                self.knowledge_network[other_agent.unique_id] = []
            if concept not in self.knowledge_network[other_agent.unique_id]:
                self.knowledge_network[other_agent.unique_id].append(concept)
        
        return shared_concepts

    def knows_agent_has_knowledge(self, agent_id: int, concept: str) -> bool:
        """Check if we know that a specific agent has a specific knowledge concept."""
        return (agent_id in self.knowledge_network and 
                concept in self.knowledge_network[agent_id])

    def get_agents_with_knowledge(self, concept: str) -> List[int]:
        """Get list of agent IDs that we know have a specific knowledge concept."""
        return [agent_id for agent_id, concepts in self.knowledge_network.items() 
                if concept in concepts]