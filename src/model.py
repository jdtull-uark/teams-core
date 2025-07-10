import mesa
import random
from typing import Dict
from .types import Task, TaskStatus
from .agents import EngineerAgent, ManagerAgent
from .rules import PsychologicalSafetyRule

class EngineeringTeamModel(mesa.Model):
    """Main model class for the engineering team simulation."""
    
    def __init__(self, num_engineers: int = 5, num_managers: int = 1, initial_tasks: int = 10,
                 initial_psych_safety: float = 0.5, psych_safety_threshold: float = 0.7):
        super().__init__()
        
        self.num_engineers = num_engineers
        self.num_managers = num_managers
        self.initial_tasks = initial_tasks
        
        # Configuration parameters
        self.base_work_units_per_step = 1.0
        
        # Psychological Safety attributes (needed for the rule to evaluate)
        self.psychological_safety: float = initial_psych_safety 
        self.psychological_safety_threshold: float = psych_safety_threshold 
        
        # Instantiate rules
        self.psychological_safety_rule = PsychologicalSafetyRule(self) # The model instantiates the rule
        
        # Task management
        self.tasks: Dict[str, Task] = {}
        
        # Create agents
        self._create_agents()
        
        # Create initial tasks
        self._create_initial_tasks(self.initial_tasks)
        
        # Basic data collection
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Completed_Tasks": lambda m: len([t for t in m.tasks.values() 
                                                  if t.status == TaskStatus.COMPLETED]),
                "Active_Tasks": lambda m: len([t for t in m.tasks.values() 
                                               if t.status == TaskStatus.IN_PROGRESS]),
                "Backlog_Tasks": lambda m: len([t for t in m.tasks.values()
                                                if t.status == TaskStatus.BACKLOG]),
                "Total_Tasks_Created": lambda m: len(m.tasks),
                "Psychological_Safety": "psychological_safety"
            },
            agent_reporters={}
        )
        # Collect initial state
        self.datacollector.collect(self)
        
    def _create_agents(self):
        """Create engineer and manager agents."""
        agent_id = 0
        
        # Create engineers
        for i in range(self.num_engineers):
            agent = EngineerAgent(agent_id, self)
            agent_id += 1
        
        # Create managers
        for i in range(self.num_managers):
            agent = ManagerAgent(agent_id, self)
            self.agents.add(agent)
            agent_id += 1
            
    def _create_initial_tasks(self, num_tasks: int):
        """Create initial set of tasks."""
        for i in range(num_tasks):
            task = Task(name=f"Task {i+1}")
            self.tasks[task.id] = task

    def _generate_new_task(self):
        """Generates a new task occasionally."""
        pass # Placeholder, no task generation for now.
        
    def step(self):
        """Execute one step of the model."""
               
        # Step all agents
        self.agents.shuffle_do("step")

        # Collect data
        self.datacollector.collect(self)