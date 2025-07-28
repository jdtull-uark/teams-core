"""
Utilities for the engineering simulation.
"""

import os
from pathlib import Path

from .model import EngineeringTeamModel
from src.framework.core.config import ModelConfig
from ..framework.core.registry import registry
from . import agents, behaviors, interactions, tasks, rules

def register_engineering_components():
    """Register all engineering components with the global registry."""
    
    # Register agent types
    registry.register_agent_type("EngineerAgent", agents.EngineerAgent)
    # registry.register_agent_type("ManagerAgent", agents.ManagerAgent)
    
    # Register behaviors
    registry.register_behavior("WorkBehavior", behaviors.WorkBehavior)
    registry.register_behavior("LearnBehavior", behaviors.LearnBehavior)
    registry.register_behavior("CollaborationBehavior", behaviors.CollaborationBehavior)
    registry.register_behavior("MovementBehavior", behaviors.MovementBehavior)
    
    # Register interaction handlers
    registry.register_interaction_handler("KnowledgeShareHandler", interactions.KnowledgeShareHandler)
    registry.register_interaction_handler("HelpRequestHandler", interactions.HelpRequestHandler)
    
    # Register task generators
    registry.register_task_generator("EngineeringTaskGenerator", tasks.EngineeringTaskGenerator)
    
    # Register rules
    registry.register_rule("PsychologicalSafetyRule", rules.PsychologicalSafetyRule)
    registry.register_rule("ProductivityRule", rules.ProductivityRule)

def create_example_project(project_name: str = "my_engineering_sim"):
    """Create an example project structure."""
    
    project_path = Path(project_name)
    project_path.mkdir(exist_ok=True)
    
    # Create directory structure
    (project_path / "configs").mkdir(exist_ok=True)
    (project_path / "custom_agents").mkdir(exist_ok=True)
    (project_path / "custom_behaviors").mkdir(exist_ok=True)
    (project_path / "results").mkdir(exist_ok=True)
    (project_path / "logs").mkdir(exist_ok=True)
    
    # Create example configuration
    config_content = """
# Example configuration for engineering team simulation
num_steps: 200
grid_width: 15
grid_height: 15
enable_logging: true

agents:
  EngineerAgent:
    count: 8
    behaviors:
      - type: WorkBehavior
      - type: LearnBehavior
      - type: CollaborationBehavior
      - type: MovementBehavior
  
  ManagerAgent:
    count: 1
    behaviors: []

interaction_handlers:
  - name: knowledge_handler
    type: KnowledgeShareHandler
  - name: help_handler
    type: HelpRequestHandler

task_generators:
  - type: EngineeringTaskGenerator
    params:
      task_creation_rate: 0.03
      max_tasks: 30

rules:
  - type: PsychologicalSafetyRule
    params:
      base_change_rate: 0.02
      threshold: 0.75
  - type: ProductivityRule

model_reporters:
  Completed_Tasks: "len([t for t in m.tasks.values() if t.status.value == 'completed'])"
  Active_Tasks: "len([t for t in m.tasks.values() if t.status.value == 'in_progress'])"
  Psychological_Safety: "m.psychological_safety"
  Average_Knowledge: "sum([len(getattr(a, 'learned_knowledge', set())) for a in m.agents]) / len(m.agents) if m.agents else 0"

agent_reporters:
  PPS: "getattr(a, 'perceived_psychological_safety', None)"
  Knowledge_Count: "len(getattr(a, 'learned_knowledge', set()))"
  Work_Efficiency: "getattr(a, 'work_efficiency', None)"
"""
    
    with open(project_path / "configs" / "default.yaml", 'w') as f:
        f.write(config_content.strip())
    
    # Create example run script
    run_script = """#!/usr/bin/env python3
'''
Example script for running an engineering team simulation.
'''

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.framework.core.config import ModelConfig
from src.engineering.model import EngineeringTeamModel
from src.engineering.utils import register_engineering_components

def main():
    # Register all engineering components
    register_engineering_components()
    
    # Load configuration
    config = ModelConfig.from_file("configs/default.yaml")
    
    # Add engineering-specific config
    config.__dict__['initial_tasks'] = 15
    config.__dict__['psychological_safety'] = 0.6
    config.__dict__['psychological_safety_threshold'] = 0.75
    
    # Create and run model
    model = EngineeringTeamModel(config)
    
    print(f"Starting simulation with {len(model.agents)} agents...")
    print(f"Initial tasks: {len(model.tasks)}")
    print(f"Knowledge space size: {len(model.knowledge_space)}")
    
    # Run simulation
    model.run_model()
    
    # Print results
    print(f"\\nSimulation completed after {model.step_count} steps")
    
    # Get final data
    final_data = model.datacollector.get_model_vars_dataframe()
    if not final_data.empty:
        print(f"Final completed tasks: {final_data['Completed_Tasks'].iloc[-1]}")
        print(f"Final psychological safety: {final_data['Psychological_Safety'].iloc[-1]:.3f}")
        print(f"Average knowledge per agent: {final_data['Average_Knowledge'].iloc[-1]:.1f}")
    
    # Save results
    model.datacollector.get_model_vars_dataframe().to_csv("results/model_data.csv")
    model.datacollector.get_agent_vars_dataframe().to_csv("results/agent_data.csv")
    
    print("Results saved to results/ directory")

if __name__ == "__main__":
    main()
"""
    
    with open(project_path / "run_simulation.py", 'w') as f:
        f.write(run_script.strip())
    
    # Make it executable
    os.chmod(project_path / "run_simulation.py", 0o755)
    
    # Create example custom agent
    custom_agent = """
from src.framework.core.agent import BaseAgent
from src.engineering.agents import EngineerAgent

class CreativeEngineerAgent(EngineerAgent):
    '''An engineer with enhanced creativity and innovation capabilities.'''
    
    def __init__(self, unique_id: int, model):
        super().__init__(unique_id, model)
        self.creativity_level = random.uniform(0.5, 1.0)
        self.innovation_bonus = 0.2
        
        # Boost work efficiency based on creativity
        self.work_efficiency *= (1 + self.creativity_level * self.innovation_bonus)
    
    def step(self):
        super().step()
        
        # Creative agents occasionally have breakthrough moments
        if random.random() < 0.01 * self.creativity_level:
            self.log_action("creative_breakthrough", {
                "creativity_level": self.creativity_level
            })
            # Boost motivation temporarily
            self.motivation = min(1.0, self.motivation + 0.1)
"""
    
    with open(project_path / "custom_agents" / "creative_engineer.py", 'w') as f:
        f.write(custom_agent.strip())
    
    # Create README
    readme = f"""# {project_name.title()}

An engineering team simulation built with the agent-based modeling framework.

## Getting Started

1. Install dependencies:
   ```bash
   pip install mesa pyyaml
   ```

2. Run the simulation:
   ```bash
   python run_simulation.py
   ```

3. View results in the `results/` directory and logs in `logs/`

## Customization

- Modify `configs/default.yaml` to change simulation parameters
- Add custom agents in `custom_agents/`
- Add custom behaviors in `custom_behaviors/`
- Check `logs/` for detailed simulation logs

## Directory Structure

- `configs/` - Configuration files
- `custom_agents/` - Custom agent implementations  
- `custom_behaviors/` - Custom behavior implementations
- `results/` - Simulation output data
- `logs/` - Detailed simulation logs
"""
    
    with open(project_path / "README.md", 'w') as f:
        f.write(readme.strip())
    
    print(f"Created example project in {project_path}/")
    print("Run 'python run_simulation.py' to start the simulation.")

# Example CLI interface
def create_cli():
    """Create a command-line interface for the engineering simulation."""
    import click
    
    @click.group()
    def cli():
        """Engineering Team Simulation Framework"""
        pass
    
    @cli.command()
    @click.option('--config', '-c', default='configs/default.yaml', 
                  help='Configuration file path')
    @click.option('--steps', '-s', default=None, type=int,
                  help='Number of simulation steps')
    @click.option('--output', '-o', default='results/',
                  help='Output directory for results')
    def run(config, steps, output):
        """Run a simulation with the specified configuration."""
        register_engineering_components()
        
        config_obj = ModelConfig.from_file(config)
        if steps:
            config_obj.num_steps = steps
        
        # Add engineering-specific defaults
        config_obj.__dict__.setdefault('initial_tasks', 10)
        config_obj.__dict__.setdefault('psychological_safety', 0.5)
        config_obj.__dict__.setdefault('psychological_safety_threshold', 0.7)
        
        model = EngineeringTeamModel(config_obj)
        model.run_model()
        
        # Save results
        Path(output).mkdir(exist_ok=True)
        model.datacollector.get_model_vars_dataframe().to_csv(f"{output}/model_data.csv")
        model.datacollector.get_agent_vars_dataframe().to_csv(f"{output}/agent_data.csv")
        
        click.echo(f"Simulation completed. Results saved to {output}/")
    
    @cli.command()
    @click.argument('project_name')
    def create_project(project_name):
        """Create a new simulation project."""
        create_example_project(project_name)
        click.echo(f"Created new project: {project_name}")
    
    @cli.command()
    def list_components():
        """List all available components."""
        register_engineering_components()
        components = registry.get_available_components()
        
        for category, items in components.items():
            click.echo(f"\n{category.title()}:")
            for item in items:
                click.echo(f"  - {item}")
    
    return cli

if __name__ == "__main__":
    cli = create_cli()
    cli()