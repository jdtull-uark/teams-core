"""Extended model with psychological safety features."""

from typing import Dict, List
from src.engineering.model import EngineeringTeamModel, create_engineering_config
from src.framework.core.config import ModelConfig
from src.framework.core.registry import registry
from .extended_agents import PsychSafetyEngineerAgent

class PsychSafetyEngineeringModel(EngineeringTeamModel):
    """Engineering team model extended with psychological safety and team efficacy."""
    
    def __init__(self,
                 num_engineers: int = 5,
                 num_managers: int = 0,
                 initial_tasks: int = 10,
                 num_steps: int = 100,
                 psychological_safety: float = 0.5,
                 contributed_psychological_safety: float = 0,
                 grid_size: int = 10,
                 enable_logging: bool = True,
                 verbose: bool = False,
                 random_seed: int = None):
        """Create a model instance with psychological safety features."""
        
        # Store psych safety parameters before calling parent
        self.psychological_safety = psychological_safety
        self.contributed_psychological_safety = contributed_psychological_safety
        
        # Create config with psych safety features
        config = create_psych_safety_config(
            num_engineers=num_engineers,
            num_managers=num_managers,
            initial_tasks=initial_tasks,
            num_steps=num_steps,
            psychological_safety=psychological_safety,
            contributed_psychological_safety=contributed_psychological_safety,
            grid_size=grid_size,
            enable_logging=enable_logging,
            verbose=verbose,
            random_seed=random_seed
        )
        
        # Call parent constructor with the config
        super().__init__(config=config)
        
        # Initialize psych safety for agents after they're created
        self._initialize_psych_safety()
        
        # Store initial team efficacy for comparison
        self._initial_efficacy = self._calculate_average_team_efficacy()
    
    def _initialize_psych_safety(self):
        """Initialize psychological safety attributes for all agents."""
        # Set initial perceived psychological safety for all agents
        min_psych_safety = max(0, self.psychological_safety - 0.25)
        max_psych_safety = min(1, self.psychological_safety + 0.25)
        for agent in self.agents:
            if hasattr(agent, 'perceived_psychological_safety'):
                agent.perceived_psychological_safety = self.random.uniform(min_psych_safety, max_psych_safety)
        
        # Set initial contributed psychological safety for all agents
        min_contributed_psych_safety = max(-1, self.contributed_psychological_safety - 0.5)
        max_contributed_psych_safety = min(1, self.contributed_psychological_safety + 0.5)
        for agent in self.agents:
            if hasattr(agent, 'contributed_psychological_safety'):
                agent.contributed_psychological_safety = self.random.uniform(min_contributed_psych_safety, max_contributed_psych_safety)
    
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
            self.verbose_print(f"=== SIMULATION START ===")
            self.verbose_print("=" * 25)
        
        # Call parent step method
        super().step()
        
        # Print final team efficacy when simulation ends OR on the last step
        if (not self.running or self.step_count >= self.config.num_steps):
            self.verbose_print(f"=== SIMULATION END ===")
            self.verbose_print("=" * 23)


def create_psych_safety_config(
    num_engineers: int = 5,
    num_managers: int = 0,
    initial_tasks: int = 10,
    num_steps: int = 100,
    psychological_safety: float = 0.5,
    contributed_psychological_safety: float = 0,
    enable_logging: bool = True,
    verbose: bool = True,
    grid_size: int = 10,
    random_seed: int = None
) -> ModelConfig:
    """Create a configuration with psychological safety features."""
    
    # Start with base engineering config
    config = create_engineering_config(
        num_engineers=num_engineers,
        num_managers=num_managers,
        initial_tasks=initial_tasks,
        num_steps=num_steps,
        enable_logging=enable_logging,
        verbose=verbose,
        grid_size=grid_size,
        random_seed=random_seed
    )
    
    # Override agent type to use extended agents
    config.agents["PsychSafetyEngineerAgent"] = config.agents.pop("EngineerAgent")
    
    # Add EvaluationBehavior
    config.agents["PsychSafetyEngineerAgent"]["behaviors"].append({
        "type": "EvaluationBehavior"
    })
    
    # Add PerformanceEvaluationHandler
    config.interaction_handlers.append({
        "name": "evaluation_handler",
        "type": "PerformanceEvaluationHandler",
        "params": {}
    })
    
    # Add rules
    config.rules = [
        {
            "type": "PsychologicalSafetyRule",
            "params": {
                "base_change_rate": 0.05,
            }
        },
        {
            "type": "ProductivityRule",
            "params": {}
        }
    ]
    
    # Add psych safety reporters
    config.model_reporters["Psychological_Safety"] = "m.psychological_safety"
    config.model_reporters["Average_PPS"] = "sum([getattr(a, 'perceived_psychological_safety', 0) for a in m.agents]) / len(m.agents) if m.agents else 0"
    config.model_reporters["Average_Team_Efficacy"] = "sum([getattr(a, 'perceived_team_efficacy', 0.5) for a in m.agents]) / len(m.agents) if m.agents else 0.5"
    config.model_reporters["Team_Efficacy_Std"] = "(__import__('statistics').stdev([getattr(a, 'perceived_team_efficacy', 0.5) for a in m.agents]) if len(m.agents) > 1 else 0.0)"
    
    # Add agent reporters
    config.agent_reporters["PPS"] = "getattr(a, 'perceived_psychological_safety', None)"
    config.agent_reporters["Perceived_Team_Efficacy"] = "getattr(a, 'perceived_team_efficacy', 0.5)"
    
    # Add custom attributes
    config.__dict__['psychological_safety'] = psychological_safety
    config.__dict__['contributed_psychological_safety'] = contributed_psychological_safety
    
    return config
