import mesa
import random
from statistics import mean
from typing import Dict
from .types import Task, TaskStatus, SubTask, SubTaskStatus
from .agents import EngineerAgent, ManagerAgent
from .rules import PsychologicalSafetyRule
from .utils import log

class EngineeringTeamModel(mesa.Model):
    """Main model class for the engineering team simulation."""
    
    def __init__(self, num_steps: int = 100, num_engineers: int = 5, num_managers: int = 0, initial_tasks: int = 10,
                 initial_psych_safety: float = 0.5, psych_safety_threshold: float = 0.7, enable_logging: bool = True):
        super().__init__()

        self.grid = mesa.space.MultiGrid(width = 10, height = 10, torus = False)
        self.is_logging = enable_logging

        self.num_engineers = num_engineers
        self.num_managers = num_managers
        self.initial_tasks = initial_tasks
        self.num_steps = num_steps
        
        # Configuration parameters
        self.base_work_units_per_step = 1.0
        
        # Psychological Safety attributes (needed for the rule to evaluate)
        self.psychological_safety = initial_psych_safety 
        self.psychological_safety_threshold = psych_safety_threshold 
        
        # Instantiate rules
        self.psychological_safety_rule = PsychologicalSafetyRule(self) # The model instantiates the rule

        self._create_knowledge_space()
        
        # Task management
        self.tasks: Dict[str, Task] = {}
        
        # Create agents
        self._create_agents()
        
        # Create initial tasks
        self._create_initial_tasks(self.initial_tasks)
        self._assign_initial_tasks()
        
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
                "Psychological_Safety": "psychological_safety",
                "Average_PPS": lambda m: mean([a.pps for a in m.agents if hasattr(a, "pps")]),
                "Average_Knowledge": lambda m: mean([len(a.learned_knowledge) for a in m.agents if hasattr(a, "learned_knowledge")]),
            },
            agent_reporters={
                "PPS": lambda a: a.pps if hasattr(a, "pps") else None,
                "Knowledge": lambda a: len(a.learned_knowledge) if hasattr(a, "learned_knowledge") else None,
                "Current_Task": lambda a: a.current_task.id if hasattr(a, "current_task") and a.current_task else None,
            }
        )

        # Collect initial state
        self.datacollector.collect(self)
        
        print('\n')
        print(40*'-')
        print(f"Model initialized with {self.num_engineers} engineers, {self.num_managers} managers.")
        print(f"Psychological safety threshold: {self.psychological_safety_threshold}")
        print(f"Initial tasks: {len(self.tasks)}. Initial Psych Safety: {self.psychological_safety:.2f}")
        print(f"Collecting the following data: {self.datacollector.get_model_vars_dataframe().columns}")
        print(f"Number of simulation steps to complete: {self.num_steps}")
        print(40*'-')
        print('\n')

        if self.is_logging:
            log.create_new_log_file()
            log.enable_logging()
            log.log_model_event(
                self.steps, 
                "model_initialized", 
                {
                    "num_engineers": self.num_engineers,
                    "num_steps": self.num_steps,
                    "psych_safety_threshold": self.psychological_safety_threshold
                }
            )
            log.log_model_event(
                self.steps,
                "initial_agent_setup",
                {
                    agent.unique_id: [task.name for task in agent.assigned_tasks] for agent in self.agents 
                }
            )
        else:
            log.disable_logging()
            print("Logging is disabled. No logs will be recorded during the simulation.")



    def run_model(self, steps: int):
        """Run the model for a specified number of steps."""

        log.log_model_event(
            self.steps,
            "simulation_start",
            {"planned_steps": steps}
        )
        
        try:
            for i in range(steps):
                self.step()
        except Exception as e:
            log.log_model_event(
                self.steps,
                "simulation_error",
                {"error": str(e)}
            )
            raise
        finally:
            log.log_session_end()

    def _create_agents(self):
        """Create engineer and manager agents."""
        unique_id = 0
        
        # Create engineers
        for i in range(self.num_engineers):
            
            agent = EngineerAgent(unique_id, self)
            agent.learned_knowledge = set(random.sample(self.knowledge_space, k=random.randint(1, len(self.knowledge_space))))
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

            unique_id += 1

    def _create_knowledge_space(self, size: int = 20):
        """Create knowledge sets for the model."""
        self.knowledge_space = [f"K{'0'*(len(str(size)) - len(str(i)))}{i}" for i in range(1, size + 1)]
        print(f"Knowledge space created with {len(self.knowledge_space)} knowledge items. Formatted as {next(iter(self.knowledge_space))}")

    def _create_initial_tasks(self, num_tasks: int):
        """Create initial set of tasks."""
        for i in range(num_tasks):
            difficulty = random.randint(1, 10)

            task = Task(name=f"Task {i+1}", difficulty=difficulty)

            self._create_subtasks(task, num_subtasks=difficulty)

            self.tasks[task.id] = task

    def _create_subtasks(self, task: Task, num_subtasks: int):
        """Create subtasks for a given task."""
        
        difficulty = random.randint(1, 10)

        required_knowledge = random.sample(self.knowledge_space, k=difficulty) if self.knowledge_space else []
        
        for i in range(num_subtasks):
            subtask = SubTask(name=f"{task.name} {i+1}", required_knowledge=required_knowledge, difficulty=difficulty)
            task.subtasks.append(subtask)

    def _assign_initial_tasks(self):
        """Assign initial tasks to engineers, ensuring each gets at least one."""
        engineers = [a for a in self.agents if isinstance(a, EngineerAgent)]
        tasks = list(self.tasks.values())
        
        # First, give each engineer one task
        for i, engineer in enumerate(engineers):
            if i < len(tasks):
                task = tasks[i]
                task.assigned_to = engineer.unique_id
                task.status = TaskStatus.BACKLOG
                engineer.assigned_tasks.append(task)
                print(f"Assigned {task.name} to Engineer {engineer.unique_id}")
        
        # Then randomly assign remaining tasks
        for task in tasks[len(engineers):]:
            engineer = self.random.choice(engineers)
            task.assigned_to = engineer.unique_id
            task.status = TaskStatus.BACKLOG
            engineer.assigned_tasks.append(task)
            print(f"Assigned {task.name} to Engineer {engineer.unique_id}")

    def _generate_new_task(self):
        """Generates a new task occasionally."""
        pass # Placeholder, no task generation for now.
        
    def step(self):
        """Execute one step of the model."""
        log.log_model_event(
            self.steps,
            "step_start"
        )

        if self.steps >= self.num_steps:
            self.running = False
               
        # Step all agents
        self.agents.shuffle_do("step")

        # Collect data
        self.datacollector.collect(self)

        log.log_model_event(
            self.steps,
            "step_end"
        )



    def is_done(self):
        return all(task.status == TaskStatus.COMPLETED for task in self.tasks.values())
    
    def get_agent_by_id(self, unique_id: str):
        """Get an agent by its unique ID."""
        for agent in self.agents:
            if agent.unique_id == unique_id:
                return agent
        return None
