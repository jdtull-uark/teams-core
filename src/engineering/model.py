"""
Engineering team model implementation.
"""

import random
from typing import Dict, List
from ..framework.core.model import BaseModel
from ..framework.core.config import ModelConfig
from ..framework.core.registry import registry
from .tasks import Task, SubTask, TaskStatus
from .agents import EngineerAgent, ManagerAgent

class EngineeringTeamModel(BaseModel):
    """Engineering team simulation model."""
    
    def __init__(self, config: ModelConfig):
        # Add engineering-specific attributes before calling super
        self.tasks: Dict[str, Task] = {}
        self.knowledge_space: List[str] = []
        self.psychological_safety = config.__dict__.get('psychological_safety', 0.5)
        self.psychological_safety_threshold = config.__dict__.get('psychological_safety_threshold', 0.7)
        
        super().__init__(config)
        
        # Create knowledge space
        self._create_knowledge_space()
        
        # Create initial tasks
        self._create_initial_tasks()
        
        # Assign initial tasks to engineers
        self._assign_initial_tasks()
        
        # Create agents from config
        self._create_agents()
    
    def _create_knowledge_space(self, size: int = 20):
        """Create the knowledge space for the simulation."""
        self.knowledge_space = [f"K{i:02d}" for i in range(1, size + 1)]
    
    def _create_initial_tasks(self, num_tasks: int = None):
        """Create initial set of tasks."""
        if num_tasks is None:
            num_tasks = self.config.__dict__.get('initial_tasks', 10)
        
        for i in range(num_tasks):
            difficulty = random.randint(1, 10)
            task = Task(name=f"Task {i+1}", difficulty=difficulty)
            
            # Create subtasks
            for j in range(difficulty):
                required_knowledge = random.sample(
                    self.knowledge_space,
                    k=min(random.randint(1, 3), len(self.knowledge_space))
                )
                
                subtask = SubTask(
                    name=f"{task.name} - Subtask {j+1}",
                    required_knowledge=required_knowledge,
                    required_steps=random.randint(1, 5)
                )
                task.subtasks.append(subtask)
            
            self.tasks[task.id] = task
    
    def _assign_initial_tasks(self):
        """Assign initial tasks to engineers."""
        engineers = [a for a in self.agents if isinstance(a, EngineerAgent)]
        tasks = list(self.tasks.values())
        
        if not engineers or not tasks:
            return
        
        # First, give each engineer one task
        for i, engineer in enumerate(engineers):
            if i < len(tasks):
                engineer.assign_task(tasks[i])
        
        # Then randomly assign remaining tasks
        for task in tasks[len(engineers):]:
            engineer = self.random.choice(engineers)
            engineer.assign_task(task)

# Configuration templates and utilities
def create_engineering_config(
    num_engineers: int = 5,
    num_managers: int = 1,
    initial_tasks: int = 10,
    num_steps: int = 100,
    psychological_safety: float = 0.5,
    psychological_safety_threshold: float = 0.7,
    enable_logging: bool = True
) -> ModelConfig:
    """Create a standard engineering team configuration."""
    
    config = ModelConfig(
        num_steps=num_steps,
        grid_width=10,
        grid_height=10,
        grid_torus=False,
        enable_logging=enable_logging,
        
        agents={
            "EngineerAgent": {
                "count": num_engineers,
                "params": {},
                "behaviors": [
                    {"type": "WorkBehavior"},
                    {"type": "LearnBehavior"},
                    {"type": "CollaborationBehavior"},
                    {"type": "MovementBehavior"}
                ]
            },
            "ManagerAgent": {
                "count": num_managers,
                "params": {},
                "behaviors": []
            }
        },
        
        interaction_handlers=[
            {
                "name": "knowledge_handler",
                "type": "KnowledgeShareHandler",
                "params": {}
            },
            {
                "name": "help_handler", 
                "type": "HelpRequestHandler",
                "params": {}
            }
        ],
        
        task_generators=[
            {
                "type": "EngineeringTaskGenerator",
                "params": {
                    "task_creation_rate": 0.05,
                    "max_tasks": 20
                }
            }
        ],
        
        rules=[
            {
                "type": "PsychologicalSafetyRule",
                "params": {
                    "base_change_rate": 0.01,
                    "threshold": psychological_safety_threshold
                }
            },
            {
                "type": "ProductivityRule",
                "params": {}
            }
        ],
        
        model_reporters={
            "Completed_Tasks": "len([t for t in m.tasks.values() if t.status.value == 'completed'])",
            "Active_Tasks": "len([t for t in m.tasks.values() if t.status.value == 'in_progress'])",
            "Backlog_Tasks": "len([t for t in m.tasks.values() if t.status.value == 'backlog'])",
            "Total_Tasks": "len(m.tasks)",
            "Psychological_Safety": "m.psychological_safety",
            "Average_PPS": "sum([getattr(a, 'perceived_psychological_safety', 0) for a in m.agents]) / len(m.agents) if m.agents else 0",
            "Average_Knowledge": "sum([len(getattr(a, 'learned_knowledge', set())) for a in m.agents]) / len(m.agents) if m.agents else 0"
        },
        
        agent_reporters={
            "PPS": "getattr(a, 'perceived_psychological_safety', None)",
            "Knowledge_Count": "len(getattr(a, 'learned_knowledge', set()))",
            "Current_Task": "getattr(a, 'current_task', None)",
            "Work_Efficiency": "getattr(a, 'work_efficiency', None)",
            "Motivation": "getattr(a, 'motivation', None)"
        }
    )
    
    # Add custom attributes
    config.__dict__['initial_tasks'] = initial_tasks
    config.__dict__['psychological_safety'] = psychological_safety
    config.__dict__['psychological_safety_threshold'] = psychological_safety_threshold
    
    return config