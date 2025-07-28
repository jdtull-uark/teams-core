"""
Engineering-specific components for agents.
"""

import random
from typing import Set, List, Dict, Any, Optional
from ..framework.interfaces import Component
from .tasks import Task, SubTask, TaskStatus, SubTaskStatus

class TaskManager(Component):
    """Manages tasks and subtasks for an agent."""
    
    def __init__(self):
        self.assigned_tasks: List[Task] = []
        self.current_task: Optional[Task] = None
        self.current_subtask: Optional[SubTask] = None
        self.completed_tasks: List[str] = []
        self.completed_subtasks: List[str] = []
        self.all_tasks_completed = False
        self.owner = None
    
    def initialize(self, owner) -> None:
        self.owner = owner
    
    def step(self) -> None:
        """Execute task management logic."""
        if not self.all_tasks_completed:
            self._work_on_current_task()
    
    def assign_task(self, task: Task) -> None:
        """Assign a new task."""
        self.assigned_tasks.append(task)
        task.assign(str(self.owner.unique_id))
    
    def _work_on_current_task(self) -> None:
        """Work on the current task or start a new one."""
        # Start a new task if needed
        if not self.current_task:
            self._start_next_task()
        
        if self.current_task and self.current_task.status == TaskStatus.IN_PROGRESS:
            if not self.current_subtask:
                self.current_subtask = self._get_next_subtask()
            
            if self.current_subtask:
                self._work_on_current_subtask()
    
    def _start_next_task(self) -> bool:
        """Start the next available task."""
        next_task = self._get_next_available_task()
        if next_task:
            self.current_task = next_task
            self.current_task.start()
            self.owner.log_action("task_started", {"task_id": self.current_task.id})
            return True
        return False
    
    def _get_next_available_task(self) -> Optional[Task]:
        """Get the next available task from backlog."""
        return next(
            (task for task in self.assigned_tasks if task.status == TaskStatus.BACKLOG),
            None
        )
    
    def _get_next_subtask(self) -> Optional[SubTask]:
        """Get the next subtask to work on."""
        if not self.current_task:
            return None
        
        # Find an in-progress subtask
        active_subtask = next(
            (subtask for subtask in self.current_task.subtasks
             if subtask.status == SubTaskStatus.IN_PROGRESS),
            None
        )
        
        if active_subtask:
            return active_subtask
        
        # Start the first available unstarted subtask
        for subtask in self.current_task.subtasks:
            if subtask.status == SubTaskStatus.NOT_STARTED:
                try:
                    subtask.start()
                    return subtask
                except ValueError:
                    continue
        
        return None
    
    def _work_on_current_subtask(self) -> None:
        """Work on the current subtask."""
        if not self.current_subtask:
            return
        
        # Check if we have required knowledge
        knowledge_manager = self.owner.get_component("knowledge_manager")
        if knowledge_manager and not knowledge_manager.has_all_required_knowledge(
            self.current_subtask.required_knowledge
        ):
            # Need to learn - this would trigger learning behavior
            self.owner.log_action("learning_required", {
                "subtask_id": self.current_subtask.id,
                "missing_knowledge": knowledge_manager.get_missing_knowledge(
                    self.current_subtask.required_knowledge
                )
            })
            return
        
        # Make progress on subtask
        progress_increment = self.owner.work_efficiency * 0.1
        self.current_subtask.progress += progress_increment
        
        if self.current_subtask.progress >= 1.0:
            self._complete_current_subtask()
    
    def _complete_current_subtask(self) -> None:
        """Complete the current subtask."""
        if not self.current_subtask:
            return
        
        try:
            self.current_subtask.complete()
            self.completed_subtasks.append(self.current_subtask.id)
            self.owner.log_action("subtask_completed", {
                "subtask_id": self.current_subtask.id
            })
            
            self.current_subtask = None
            self._check_task_completion()
        except ValueError as e:
            self.owner.log_action("subtask_completion_failed", {
                "subtask_id": self.current_subtask.id,
                "error": str(e)
            })
    
    def _check_task_completion(self) -> None:
        """Check if current task is completed."""
        if not self.current_task:
            return
        
        if all(subtask.status == SubTaskStatus.COMPLETED 
               for subtask in self.current_task.subtasks):
            try:
                self.current_task.complete()
                self.completed_tasks.append(self.current_task.id)
                self.owner.log_action("task_completed", {"task_id": self.current_task.id})
                self.current_task = None
                
                # Check if all tasks are completed
                if all(task.status == TaskStatus.COMPLETED for task in self.assigned_tasks):
                    self.all_tasks_completed = True
                    self.owner.log_action("all_tasks_completed", {
                        "engineer_id": self.owner.unique_id
                    })
            except ValueError as e:
                self.owner.log_action("task_completion_failed", {
                    "task_id": self.current_task.id,
                    "error": str(e)
                })

class KnowledgeManager(Component):
    """Manages knowledge learning and sharing for an agent."""
    
    def __init__(self):
        self.learned_knowledge: Set[str] = set()
        self.concept_learning_progress: Dict[str, float] = {}
        self.knowledge_network: Dict[str, Set[str]] = {}  # agent_id -> knowledge they have
        self.owner = None
    
    def initialize(self, owner) -> None:
        self.owner = owner
    
    def step(self) -> None:
        """Execute knowledge management logic."""
        # Continue learning concepts in progress
        concepts_to_complete = []
        for concept, progress in self.concept_learning_progress.items():
            if self._continue_learning(concept):
                concepts_to_complete.append(concept)
        
        # Complete learned concepts
        for concept in concepts_to_complete:
            self.learned_knowledge.add(concept)
            del self.concept_learning_progress[concept]
            self.owner.log_action("knowledge_learned", {"concept": concept})
    
    def learn_concept(self, concept: str) -> bool:
        """Start or continue learning a concept."""
        if concept in self.learned_knowledge:
            return True
        
        if concept not in self.concept_learning_progress:
            self.concept_learning_progress[concept] = 0.0
        
        return self._continue_learning(concept)
    
    def _continue_learning(self, concept: str) -> bool:
        """Continue learning a concept and return True if completed."""
        if concept in self.learned_knowledge:
            return True
        
        learning_rate = getattr(self.owner, 'learning_rate', 0.05)
        work_efficiency = getattr(self.owner, 'work_efficiency', 1.0)
        
        progress_increment = (
            learning_rate * 
            work_efficiency * 
            random.uniform(0.5, 1.5)
        )
        
        self.concept_learning_progress[concept] += progress_increment
        return self.concept_learning_progress[concept] >= 1.0
    
    def receive_shared_knowledge(self, sender_id: str, concept: str) -> bool:
        """Receive knowledge shared from another agent."""
        if concept not in self.learned_knowledge:
            self.learned_knowledge.add(concept)
            self._update_knowledge_network(sender_id, concept)
            self.owner.log_action("knowledge_share_received", {
                "sender_id": sender_id,
                "shared_concept": concept
            })
            return True
        else:
            self._update_knowledge_network(sender_id, concept)
            return False
    
    def _update_knowledge_network(self, agent_id: str, concept: str) -> None:
        """Update knowledge about what other agents know."""
        if agent_id not in self.knowledge_network:
            self.knowledge_network[agent_id] = set()
        self.knowledge_network[agent_id].add(concept)
    
    def get_missing_knowledge(self, required_concepts: List[str] = None) -> List[str]:
        """Get missing knowledge concepts."""
        if required_concepts is None:
            task_manager = self.owner.get_component("task_manager")
            if task_manager and task_manager.current_subtask:
                required_concepts = task_manager.current_subtask.required_knowledge
            else:
                return []
        
        return [concept for concept in required_concepts 
                if concept not in self.learned_knowledge]
    
    def has_all_required_knowledge(self, required_concepts: List[str] = None) -> bool:
        """Check if agent has all required knowledge."""
        missing = self.get_missing_knowledge(required_concepts)
        return len(missing) == 0
    
    def get_shareable_knowledge(self, requested_concepts: List[str]) -> List[str]:
        """Get concepts that can be shared from the requested list."""
        return [concept for concept in requested_concepts 
                if concept in self.learned_knowledge]
    
    def find_agents_with_knowledge(self, concept: str) -> List[str]:
        """Find agents known to have specific knowledge."""
        return [agent_id for agent_id, knowledge in self.knowledge_network.items()
                if concept in knowledge]

class CommunicationManager(Component):
    """Manages communication and interactions for an agent."""
    
    def __init__(self):
        self.interaction_history: List[Dict[str, Any]] = []
        self.help_requests_made = 0
        self.help_requests_received = 0
        self.seeking_knowledge = False
        self.searching_agents = False
        self.searching_agents_targets: List[str] = []
        self.owner = None
    
    def initialize(self, owner) -> None:
        self.owner = owner
    
    def step(self) -> None:
        """Execute communication logic."""
        # Look for nearby agents to interact with
        if hasattr(self.owner.model, 'space'):
            neighbors = self.owner.model.space.get_neighbors(
                self.owner.position, moore=True, include_center=False
            )
            
            if neighbors:
                self._attempt_interaction(neighbors)
    
    def _attempt_interaction(self, neighbors) -> None:
        """Attempt to interact with nearby agents."""
        recipient = None
        interaction_type = None
        
        # Determine interaction based on current needs
        if self.searching_agents and any(
            str(agent.unique_id) in self.searching_agents_targets 
            for agent in neighbors
        ):
            recipient = next((
                agent for agent in neighbors 
                if str(agent.unique_id) in self.searching_agents_targets
            ), None)
            interaction_type = "help_request"
        
        elif self.seeking_knowledge:
            recipient = random.choice(neighbors)
            interaction_type = "knowledge_request"
        
        elif self.owner.current_task:
            recipient = random.choice(neighbors)
            interaction_type = "collaboration"
        
        if recipient and hasattr(recipient, 'unique_id'):
            success = self.owner.interact_with(recipient, interaction_type)
            if success:
                self.interaction_history.append({
                    "step": self.owner.model.steps,
                    "type": interaction_type,
                    "recipient": recipient.unique_id,
                    "success": success
                })