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
    
    def __init__(self, 
                 num_engineers: int = 5,
                 num_managers: int = 1,
                 initial_tasks: int = 10,
                 num_steps: int = 100,
                 psychological_safety: float = 0.5,
                 psychological_safety_threshold: float = 0.7,
                 grid_size: int = 10,
                 enable_logging: bool = True):
        """Create a model instance directly from parameters."""
        # Create config from parameters
        config = create_engineering_config(
            num_engineers=num_engineers,
            num_managers=num_managers,
            initial_tasks=initial_tasks,
            num_steps=num_steps,
            psychological_safety=psychological_safety,
            psychological_safety_threshold=psychological_safety_threshold,
            grid_size=grid_size,
            enable_logging=enable_logging
        )
        
        # Add engineering-specific attributes before calling super
        self.tasks: Dict[str, Task] = {}
        self.knowledge_space: List[str] = []
        self.psychological_safety = config.__dict__.get('psychological_safety', 0.5)
        self.psychological_safety_threshold = config.__dict__.get('psychological_safety_threshold', 0.7)
        
        super().__init__(config)
        
        # Create knowledge space
        self._create_knowledge_space()
        
        # Create agents from config
        self._create_agents()

        # Create initial tasks
        self._create_initial_tasks()
        
        # Assign initial tasks to engineers
        self._assign_initial_tasks()
        
        # Store initial team efficacy for comparison
        self._initial_efficacy = self._calculate_average_team_efficacy()
    
    def _calculate_average_team_efficacy(self) -> float:
        """Calculate the current average team efficacy."""
        if not self.agents:
            return 0.5
        total = sum(getattr(agent, 'perceived_team_efficacy', 0.5) for agent in self.agents)
        return total / len(self.agents)

    def step(self) -> None:
        """Execute one model step with team efficacy logging."""
        # Print initial team efficacy on first step
        if self.step_count == 0:
            initial_efficacy = self._calculate_average_team_efficacy()
            print(f"=== SIMULATION START ===")
            print(f"Starting Average Perceived Team Efficacy: {initial_efficacy:.3f}")
            print(f"Individual agent team efficacy values:")
            for agent in self.agents:
                pte = getattr(agent, 'perceived_team_efficacy', 0.5)
                print(f"  Agent {agent.unique_id}: {pte:.3f}")
            print("=" * 25)
        
        # Call parent step method
        super().step()
        
        # Print final team efficacy when simulation ends OR on the last step
        if not self.running or self.step_count >= self.config.num_steps:
            final_efficacy = self._calculate_average_team_efficacy()
            print(f"=== SIMULATION END ===")
            print(f"Final Average Perceived Team Efficacy: {final_efficacy:.3f}")
            print(f"Individual agent team efficacy values:")
            for agent in self.agents:
                pte = getattr(agent, 'perceived_team_efficacy', 0.5)
                print(f"  Agent {agent.unique_id}: {pte:.3f}")
            
            # Calculate change
            if hasattr(self, '_initial_efficacy'):
                change = final_efficacy - self._initial_efficacy
                print(f"Change in Team Efficacy: {change:+.3f}")
            print("=" * 23)
    
    @classmethod
    def from_config(cls, config: ModelConfig) -> 'EngineeringTeamModel':
        """Create a model instance from a ModelConfig object."""
        # Extract parameters from config
        num_engineers = 5  # default
        num_managers = 0   # default
        initial_tasks = config.__dict__.get('initial_tasks', 10)
        psychological_safety = config.__dict__.get('psychological_safety', 0.5)
        psychological_safety_threshold = config.__dict__.get('psychological_safety_threshold', 0.7)
        
        # Extract from agents config
        if 'EngineerAgent' in config.agents:
            num_engineers = config.agents['EngineerAgent'].get('count', 5)
        if 'ManagerAgent' in config.agents:
            num_managers = config.agents['ManagerAgent'].get('count', 0)
        
        # Create instance using parameter-based constructor
        instance = cls.__new__(cls)  # Create instance without calling __init__
        
        # Add engineering-specific attributes before calling super
        instance.tasks = {}
        instance.knowledge_space = []
        instance.psychological_safety = psychological_safety
        instance.psychological_safety_threshold = psychological_safety_threshold
        
        # Call BaseModel.__init__ directly
        BaseModel.__init__(instance, config)
        
        # Create knowledge space
        instance._create_knowledge_space()
        
        # Create agents from config
        instance._create_agents()

        # Create initial tasks
        instance._create_initial_tasks()
        
        # Assign initial tasks to engineers
        instance._assign_initial_tasks()
        
        return instance
        
    
    def _create_knowledge_space(self, size: int = 20):
        """Create the knowledge space for the simulation."""
        self.knowledge_space = [f"K{i:02d}" for i in range(1, size + 1)]
        
    def _distribute_initial_knowledge(self, agent: EngineerAgent):
        """Distribute initial knowledge to an agent."""
        # Each agent starts with 1 to 1/5 of total knowledge
        num_knowledge = self.random.randint(1, len(self.knowledge_space) // 5)
        initial_knowledge = set(self.random.sample(self.knowledge_space, k=num_knowledge))
        
        # Get the knowledge manager component and add the knowledge
        knowledge_manager = agent.get_component("knowledge_manager")
        if knowledge_manager:
            knowledge_manager.learned_knowledge.update(initial_knowledge)
            print(f"Agent {agent.unique_id} initialized with {len(initial_knowledge)} knowledge items")

    def _create_agents(self):
        """Create agents from configuration."""
        super()._create_agents()

        # Distribute initial knowledge to all engineer agents
        for agent in self.agents:
            if isinstance(agent, EngineerAgent):
                self._distribute_initial_knowledge(agent)

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
        
        # Print a clean summary of task assignments
        self._print_task_assignment_summary()
    
    def _print_task_assignment_summary(self):
        """Print a clean summary of task assignments."""
        print("=== INITIAL TASK ASSIGNMENTS ===")
        engineers = [a for a in self.agents if isinstance(a, EngineerAgent)]
        for engineer in engineers:
            task_manager = engineer.get_component("task_manager")
            if task_manager and task_manager.assigned_tasks:
                task_names = [f"'{t.name}' (diff: {t.difficulty})" for t in task_manager.assigned_tasks]
                print(f"Agent {engineer.unique_id}: {len(task_manager.assigned_tasks)} tasks - {', '.join(task_names)}")
            else:
                print(f"Agent {engineer.unique_id}: No tasks assigned")
        print("=" * 33)

# Configuration templates and utilities
def create_engineering_config(
    num_engineers: int = 5,
    num_managers: int = 0,
    initial_tasks: int = 10,
    num_steps: int = 100,
    psychological_safety: float = 0.5,
    psychological_safety_threshold: float = 0.7,
    enable_logging: bool = True,
    grid_size: int = 10
) -> ModelConfig:
    """Create a standard engineering team configuration."""
    
    config = ModelConfig(
        num_steps=num_steps,
        grid_width=grid_size,
        grid_height=grid_size,
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
                    {"type": "MovementBehavior"},
                    {"type": "EvaluationBehavior"}
                ]
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
            },
            {
                "name": "evaluation_handler",
                "type": "PerformanceEvaluationHandler",
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
            "Average_Knowledge": "sum([len(getattr(a, 'learned_knowledge', set())) for a in m.agents]) / len(m.agents) if m.agents else 0",
            "Average_Team_Efficacy": "sum([getattr(a, 'perceived_team_efficacy', 0.5) for a in m.agents]) / len(m.agents) if m.agents else 0.5",
            "Team_Efficacy_Std": "(__import__('statistics').stdev([getattr(a, 'perceived_team_efficacy', 0.5) for a in m.agents]) if len(m.agents) > 1 else 0.0)"
        },
        
        agent_reporters={
            "PPS": "getattr(a, 'perceived_psychological_safety', None)",
            "Knowledge_Count": "len(getattr(a, 'learned_knowledge', set()))",
            "Current_Task": "getattr(a, 'current_task', None)",
            "Work_Efficiency": "getattr(a, 'work_efficiency', None)",
            "Motivation": "getattr(a, 'motivation', None)",
            "Perceived_Team_Efficacy": "getattr(a, 'perceived_team_efficacy', 0.5)"
        }
    )
    
    # Add ManagerAgent if needed
    if num_managers > 0:
        config.agents["ManagerAgent"] = {
            "count": num_managers,
            "params": {},
            "behaviors": []
        }
    
    # Add custom attributes
    config.__dict__['initial_tasks'] = initial_tasks
    config.__dict__['psychological_safety'] = psychological_safety
    config.__dict__['psychological_safety_threshold'] = psychological_safety_threshold
    
    return config