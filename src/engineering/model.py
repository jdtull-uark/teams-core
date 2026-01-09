"""
Engineering team model implementation.
"""

import random
from typing import Dict, List
from ..framework.core.model import BaseModel
from ..framework.core.config import ModelConfig
from ..framework.core.registry import registry
from .tasks import Task, SubTask, TaskStatus
from .agents import EngineerAgent

class EngineeringTeamModel(BaseModel):
    """Engineering team simulation model."""
    
    def __init__(self, 
                 config: ModelConfig = None,
                 num_engineers: int = 5,
                 num_managers: int = 0,
                 initial_tasks: int = 10,
                 num_steps: int = 100,
                 grid_size: int = 10,
                 enable_logging: bool = True,
                 verbose: bool = False,
                 print_progress_bar: bool = True,
                 random_seed: int = None):
        """Create a model instance from config or parameters.
        
        Args:
            config: Optional ModelConfig. If provided, all other parameters are ignored.
            num_engineers: Number of engineer agents
            num_managers: Number of manager agents
            initial_tasks: Number of initial tasks
            num_steps: Number of simulation steps
            grid_size: Size of the grid
            enable_logging: Enable logging
            verbose: Verbose output
            print_progress_bar: Show progress bar
            random_seed: Random seed
        """
        # Create config from parameters if not provided
        if config is None:
            config = create_engineering_config(
                num_engineers=num_engineers,
                num_managers=num_managers,
                initial_tasks=initial_tasks,
                num_steps=num_steps,
                grid_size=grid_size,
                enable_logging=enable_logging,
                verbose=verbose,
                random_seed=random_seed
            )
        
        # Add engineering-specific attributes before calling super
        self.tasks: Dict[str, Task] = {}
        self.knowledge_space: List[str] = []
        
        super().__init__(config)
        
        # Create knowledge space
        self._create_knowledge_space()
        
        # Create agents from config
        self._create_agents()

        # Create initial tasks
        self._create_initial_tasks()
        
        # Assign initial tasks to engineers
        self._assign_initial_tasks()
    
    def step(self) -> None:
        """Execute one model step."""
        # Print initial message on first step
        if self.step_count == 0:
            self.verbose_print(f"=== SIMULATION START ===")
            self.verbose_print("=" * 25)
        
        # Call parent step method
        super().step()
        
        # Print final message when simulation ends
        if (not self.running or self.step_count >= self.config.num_steps):
            self.verbose_print(f"=== SIMULATION END ===")
            self.verbose_print("=" * 23)
    
    def _create_knowledge_space(self, size: int = 100):
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
            self.verbose_print(f"Agent {agent.unique_id} initialized with {len(initial_knowledge)} knowledge items")

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
            difficulty = self.random.randint(1, 10)
            task = Task(name=f"Task {i+1}", difficulty=difficulty)
            
            # Create subtasks
            for j in range(difficulty):
                required_knowledge = self.random.sample(
                    self.knowledge_space,
                    k=min(self.random.randint(1, 3), len(self.knowledge_space))
                )
                
                subtask = SubTask(
                    name=f"{task.name} - Subtask {j+1}",
                    required_knowledge=required_knowledge,
                    required_steps=self.random.randint(1, 5)
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
        if not self.verbose:
            return
            
        self.verbose_print("=== INITIAL TASK ASSIGNMENTS ===")
        engineers = [a for a in self.agents if isinstance(a, EngineerAgent)]
        for engineer in engineers:
            task_manager = engineer.get_component("task_manager")
            if task_manager and task_manager.assigned_tasks:
                task_names = [f"'{t.name}' (diff: {t.difficulty})" for t in task_manager.assigned_tasks]
                self.verbose_print(f"Agent {engineer.unique_id}: {len(task_manager.assigned_tasks)} tasks - {', '.join(task_names)}")
            else:
                self.verbose_print(f"Agent {engineer.unique_id}: No tasks assigned")
        self.verbose_print("=" * 33)

# Configuration templates and utilities
def create_engineering_config(
    num_engineers: int = 5,
    num_managers: int = 0,
    initial_tasks: int = 10,
    num_steps: int = 100,
    enable_logging: bool = True,
    verbose: bool = True,
    grid_size: int = 10,
    random_seed: int = None
) -> ModelConfig:
    """Create a standard engineering team configuration."""
    
    config = ModelConfig(
        num_steps=num_steps,
        grid_width=grid_size,
        grid_height=grid_size,
        grid_torus=False,
        enable_logging=enable_logging,
        random_seed=random_seed,
        
        agents={
            "EngineerAgent": {
                "count": num_engineers,
                "params": {},
                "behaviors": [
                    {"type": "WorkBehavior"},
                    {"type": "LearnBehavior"},
                    {"type": "CommunicationBehavior"},
                    {"type": "MovementBehavior"}
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
            }
        ],
        
        task_generators=[
            {
                "type": "EngineeringTaskGenerator",
                "params": {
                    "task_creation_rate": 0.0,
                    "max_tasks": 20
                }
            }
        ],
        
        rules=[],
        
        model_reporters={
            "Completed_Tasks": "len([t for t in m.tasks.values() if t.status.value == 'completed'])",
            "Active_Tasks": "len([t for t in m.tasks.values() if t.status.value == 'in_progress'])",
            "Backlog_Tasks": "len([t for t in m.tasks.values() if t.status.value == 'backlog'])",
            "Total_Tasks": "len(m.tasks)",
            "Average_Knowledge": "sum([len(getattr(a, 'learned_knowledge', set())) for a in m.agents]) / len(m.agents) if m.agents else 0"
        },
        
        agent_reporters={
            "Knowledge_Count": "len(getattr(a, 'learned_knowledge', set()))",
            "Current_Task": "getattr(a, 'current_task', None)",
            "Work_Efficiency": "getattr(a, 'work_efficiency', None)",
            "Motivation": "getattr(a, 'motivation', None)"
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
    config.__dict__['verbose'] = verbose
    
    return config