"""
Base model class with pluggable architecture.
"""

import mesa
from typing import Dict, List, Any, Optional, Type
from .registry import registry
from .config import ModelConfig
from ..interfaces import InteractionHandler, TaskGenerator, Rule

class BaseModel(mesa.Model):
    """
    Base model class with support for pluggable components and configuration.
    """
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        
        # Set random seed if provided
        if config.random_seed is not None:
            self.random.seed(config.random_seed)
        
        # Initialize space
        self.space = mesa.space.MultiGrid(
            config.grid_width, 
            config.grid_height, 
            config.grid_torus
        )
        
        # Component systems
        self.interaction_handlers: Dict[str, InteractionHandler] = {}
        self.task_generators: List[TaskGenerator] = []
        self.rules: List[Rule] = []
        
        # State tracking
        self.global_state: Dict[str, Any] = {}
        self.step_count = 0
        
        # Initialize logging if enabled
        if config.enable_logging:
            self._setup_logging()
        
        # Initialize data collection
        self._setup_data_collection()
        
        # Initialize components from config
        self._initialize_components()
        
        # Create agents from config
        self._create_agents()
    
    def _setup_logging(self) -> None:
        """Set up logging system."""
        # Import and configure logging
        from ..utils.logging import setup_logging
        setup_logging(
            log_file=self.config.log_file,
            log_level=self.config.log_level
        )
    
    def _setup_data_collection(self) -> None:
        """Set up data collection based on configuration."""
        model_reporters = {}
        agent_reporters = {}
        
        # Add configured reporters
        for name, func_str in self.config.model_reporters.items():
            model_reporters[name] = eval(f"lambda m: {func_str}")
        
        for name, func_str in self.config.agent_reporters.items():
            agent_reporters[name] = eval(f"lambda a: {func_str}")
        
        self.datacollector = mesa.DataCollector(
            model_reporters=model_reporters,
            agent_reporters=agent_reporters
        )
    
    def _initialize_components(self) -> None:
        """Initialize all components from configuration."""
        # Initialize interaction handlers
        for handler_config in self.config.interaction_handlers:
            handler_name = handler_config["name"]
            handler_type = handler_config["type"]
            handler_params = handler_config.get("params", {})
            
            handler = registry.create_interaction_handler(handler_type, **handler_params)
            for interaction_type in handler.get_supported_types():
                self.interaction_handlers[interaction_type] = handler
        
        # Initialize task generators
        for generator_config in self.config.task_generators:
            generator_type = generator_config["type"]
            generator_params = generator_config.get("params", {})
            
            generator = registry.create_task_generator(generator_type, **generator_params)
            self.task_generators.append(generator)
        
        # Initialize rules
        for rule_config in self.config.rules:
            rule_type = rule_config["type"]
            rule_params = rule_config.get("params", {})
            
            rule = registry.create_rule(rule_type, **rule_params)
            self.rules.append(rule)
    
    def _create_agents(self) -> None:
        """Create agents based on configuration."""
        agent_id = 0
        
        for agent_type, agent_config in self.config.agents.items():
            count = agent_config.get("count", 1)
            params = agent_config.get("params", {})
            behaviors = agent_config.get("behaviors", [])
            
            for _ in range(count):
                # Create agent
                agent = registry.create_agent(agent_type, agent_id, self)
                
                # Add configured behaviors
                for behavior_config in behaviors:
                    behavior_type = behavior_config["type"]
                    behavior_params = behavior_config.get("params", {})
                    behavior = registry.create_behavior(behavior_type, **behavior_params)
                    agent.add_behavior(behavior)
                
                # Add agent to model
                self.add(agent)
                
                # Place agent in space if it has spatial behavior
                if hasattr(agent, 'position') and agent.position is None:
                    x = self.random.randrange(self.space.width)
                    y = self.random.randrange(self.space.height)
                    self.space.place_agent(agent, (x, y))
                    agent.position = (x, y)
                
                agent_id += 1
    
    def handle_interaction(self, initiator, recipient, interaction_type: str, 
                          context: Dict[str, Any]) -> bool:
        """Handle an interaction between two agents."""
        if interaction_type in self.interaction_handlers:
            handler = self.interaction_handlers[interaction_type]
            return handler.handle_interaction(initiator, recipient, interaction_type, context)
        
        # Log unhandled interaction
        if hasattr(self, 'log_model_event'):
            self.log_model_event("unhandled_interaction", {
                "type": interaction_type,
                "initiator": initiator.unique_id,
                "recipient": recipient.unique_id
            })
        
        return False
    
    def step(self) -> None:
        """Execute one model step."""
        self.step_count += 1
        
        # Apply rules
        for rule in self.rules:
            if rule.should_apply(self):
                rule.apply(self)
        
        # Generate new tasks
        for generator in self.task_generators:
            if generator.should_generate(self):
                task = generator.generate_task(self)
                # Handle new task (this would be domain-specific)
        
        # Step all agents
        self.step()
        
        # Collect data
        if hasattr(self, 'datacollector'):
            self.datacollector.collect(self)
        
        # Check termination conditions
        if self.step_count >= self.config.num_steps:
            self.running = False
    
    def run_model(self, steps: Optional[int] = None) -> None:
        """Run the model for a specified number of steps."""
        if steps is None:
            steps = self.config.num_steps
        
        for _ in range(steps):
            if not self.running:
                break
            self.step()
    
    def get_agent_by_id(self, agent_id: int):
        """Get an agent by its unique ID."""
        for agent in self.agents:
            if agent.unique_id == agent_id:
                return agent
        return None
    
    def log_model_event(self, event: str, details: Dict[str, Any] = None) -> None:
        """Log a model-level event."""
        if hasattr(self, '_logger'):
            from ..utils.logging import log_model_event
            log_model_event(self.step_count, event, details)
    
    def log_agent_action(self, agent_id: int, action: str, details: Dict[str, Any] = None) -> None:
        """Log an agent action."""
        if hasattr(self, '_logger'):
            from ..utils.logging import log_agent_action
            log_agent_action(agent_id, self.step_count, action, details)