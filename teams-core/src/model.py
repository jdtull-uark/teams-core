import mesa
import random
from typing import Dict
from .types import Task, TaskStatus
from .agents import EngineerAgent, ManagerAgent

class EngineeringTeamModel(mesa.Model):
    """Main model class for the engineering team simulation."""
    
    def __init__(self, num_engineers: int = 5, num_managers: int = 1):
        super().__init__()
        
        self.num_engineers = num_engineers
        self.num_managers = num_managers
        
        # Create scheduler
        self.schedule = mesa.time.RandomActivation(self)
        
        # Task management
        self.tasks: Dict[str, Task] = {}
        
        # Create agents
        self._create_agents()
        
        # Create initial tasks
        self._create_initial_tasks(10)
        
        # Basic data collection
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Completed_Tasks": lambda m: len([t for t in m.tasks.values() 
                                                if t.status == TaskStatus.COMPLETED]),
                "Active_Tasks": lambda m: len([t for t in m.tasks.values() 
                                             if t.status == TaskStatus.IN_PROGRESS]),
            }
        )
    
    def _create_agents(self):
        """Create engineer and manager agents."""
        agent_id = 0
        
        # Create engineers
        for i in range(self.num_engineers):
            agent = EngineerAgent(agent_id, self)
            self.schedule.add(agent)
            agent_id += 1
        
        # Create managers
        for i in range(self.num_managers):
            agent = ManagerAgent(agent_id, self)
            self.schedule.add(agent)
            agent_id += 1
    
    def _create_initial_tasks(self, num_tasks: int):
        """Create initial set of tasks."""
        for i in range(num_tasks):
            task = Task(name=f"Task {i+1}")
            self.tasks[task.id] = task
    
    def step(self):
        """Execute one step of the model."""
        
        # Step all agents
        self.schedule.step()
        
        # Collect data
        self.datacollector.collect(self)