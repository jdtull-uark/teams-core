"""
Engineering-specific agent implementations.
"""

import random
from typing import Set, List, Dict, Any, Optional
from ..framework.core.agent import BaseAgent
from ..framework.core.interfaces import Component
from .components import TaskManager, KnowledgeManager, CommunicationManager

class EngineerAgent(BaseAgent):
    """An engineer agent with domain-specific attributes."""
    
    def __init__(self, unique_id: int, model):
        super().__init__(unique_id, model)
        
        # Engineer-specific attributes
        self.perceived_psychological_safety = random.uniform(0.0, 1.0)
        self.contributed_psychological_safety = random.uniform(-1.0, 1.0)
        self.learning_rate = random.uniform(0.2, 0.4)
        self.communication_skill = random.uniform(0.1, 1.0)
        self.motivation = random.uniform(0.1, 1.0)
        self.work_efficiency = random.uniform(0.5, 1.5)
        self.is_available = True
        self.perceived_team_efficacy = 0.5
        
        # Add engineering-specific components
        self.add_component("task_manager", TaskManager())
        self.add_component("knowledge_manager", KnowledgeManager())
        self.add_component("communication_manager", CommunicationManager())
        
        # Initialize with some random knowledge
        knowledge_manager = self.get_component("knowledge_manager")
        if hasattr(model, 'knowledge_space') and knowledge_manager:
            initial_knowledge = random.sample(
                model.knowledge_space, 
                k=random.randint(1, min(5, len(model.knowledge_space)))
            )
            for concept in initial_knowledge:
                knowledge_manager.learn_concept(concept)
    
    @property
    def current_task(self):
        task_manager = self.get_component("task_manager")
        return task_manager.current_task if task_manager else None
    
    @property
    def current_subtask(self):
        task_manager = self.get_component("task_manager")
        return task_manager.current_subtask if task_manager else None
    
    @property
    def learned_knowledge(self) -> Set[str]:
        knowledge_manager = self.get_component("knowledge_manager")
        return knowledge_manager.learned_knowledge if knowledge_manager else set()
    
    def assign_task(self, task) -> None:
        """Assign a task to this engineer."""
        task_manager = self.get_component("task_manager")
        if task_manager:
            task_manager.assign_task(task)
            task.assigned_to = str(self.unique_id)
    
    def get_missing_knowledge(self, required_concepts: List[str] = None) -> List[str]:
        """Get missing knowledge concepts."""
        knowledge_manager = self.get_component("knowledge_manager")
        return knowledge_manager.get_missing_knowledge(required_concepts) if knowledge_manager else []
    
    def has_all_required_knowledge(self, required_concepts: List[str] = None) -> bool:
        """Check if agent has all required knowledge."""
        knowledge_manager = self.get_component("knowledge_manager")
        return knowledge_manager.has_all_required_knowledge(required_concepts) if knowledge_manager else True

class ManagerAgent(BaseAgent):
    """A manager agent responsible for task assignment and team coordination."""
    
    def __init__(self, unique_id: int, model):
        super().__init__(unique_id, model)
        self.management_style = random.choice(['collaborative', 'directive', 'supportive'])
        self.add_component("task_manager", TaskManager())