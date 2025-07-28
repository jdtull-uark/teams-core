"""
Component registry system for managing pluggable components.
"""

from typing import Dict, Type, Any, List, Optional
import importlib
import inspect
from ..interfaces import AgentBehavior, InteractionHandler, TaskGenerator, Rule

class ComponentRegistry:
    """Registry for managing all pluggable components."""
    
    def __init__(self):
        self._agent_types: Dict[str, Type] = {}
        self._behaviors: Dict[str, Type[AgentBehavior]] = {}
        self._interaction_handlers: Dict[str, Type[InteractionHandler]] = {}
        self._task_generators: Dict[str, Type[TaskGenerator]] = {}
        self._rules: Dict[str, Type[Rule]] = {}
        self._components: Dict[str, Type] = {}
    
    def register_agent_type(self, name: str, agent_class: Type) -> None:
        """Register a new agent type."""
        self._agent_types[name] = agent_class
    
    def register_behavior(self, name: str, behavior_class: Type[AgentBehavior]) -> None:
        """Register a new behavior."""
        if not issubclass(behavior_class, AgentBehavior):
            raise ValueError(f"Behavior {name} must inherit from AgentBehavior")
        self._behaviors[name] = behavior_class
    
    def register_interaction_handler(self, name: str, handler_class: Type[InteractionHandler]) -> None:
        """Register a new interaction handler."""
        if not issubclass(handler_class, InteractionHandler):
            raise ValueError(f"Handler {name} must inherit from InteractionHandler")
        self._interaction_handlers[name] = handler_class
    
    def register_task_generator(self, name: str, generator_class: Type[TaskGenerator]) -> None:
        """Register a new task generator."""
        if not issubclass(generator_class, TaskGenerator):
            raise ValueError(f"Generator {name} must inherit from TaskGenerator")
        self._task_generators[name] = generator_class
    
    def register_rule(self, name: str, rule_class: Type[Rule]) -> None:
        """Register a new rule."""
        if not issubclass(rule_class, Rule):
            raise ValueError(f"Rule {name} must inherit from Rule")
        self._rules[name] = rule_class
    
    def register_component(self, name: str, component_class: Type) -> None:
        """Register a generic component."""
        self._components[name] = component_class
    
    def create_agent(self, agent_type: str, *args, **kwargs) -> Any:
        """Create an agent instance."""
        if agent_type not in self._agent_types:
            raise KeyError(f"Unknown agent type: {agent_type}")
        return self._agent_types[agent_type](*args, **kwargs)
    
    def create_behavior(self, behavior_name: str, *args, **kwargs) -> AgentBehavior:
        """Create a behavior instance."""
        if behavior_name not in self._behaviors:
            raise KeyError(f"Unknown behavior: {behavior_name}")
        return self._behaviors[behavior_name](*args, **kwargs)
    
    def create_interaction_handler(self, handler_name: str, *args, **kwargs) -> InteractionHandler:
        """Create an interaction handler instance."""
        if handler_name not in self._interaction_handlers:
            raise KeyError(f"Unknown interaction handler: {handler_name}")
        return self._interaction_handlers[handler_name](*args, **kwargs)
    
    def create_task_generator(self, generator_name: str, *args, **kwargs) -> TaskGenerator:
        """Create a task generator instance."""
        if generator_name not in self._task_generators:
            raise KeyError(f"Unknown task generator: {generator_name}")
        return self._task_generators[generator_name](*args, **kwargs)
    
    def create_rule(self, rule_name: str, *args, **kwargs) -> Rule:
        """Create a rule instance."""
        if rule_name not in self._rules:
            raise KeyError(f"Unknown rule: {rule_name}")
        return self._rules[rule_name](*args, **kwargs)
    
    def create_component(self, component_name: str, *args, **kwargs) -> Any:
        """Create a component instance."""
        if component_name not in self._components:
            raise KeyError(f"Unknown component: {component_name}")
        return self._components[component_name](*args, **kwargs)
    
    def load_from_module(self, module_path: str) -> None:
        """Load and register components from a module."""
        try:
            module = importlib.import_module(module_path)
            
            # Auto-discover and register components
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ == module_path:  # Only consider classes defined in this module
                    if issubclass(obj, AgentBehavior) and obj != AgentBehavior:
                        self.register_behavior(name, obj)
                    elif issubclass(obj, InteractionHandler) and obj != InteractionHandler:
                        self.register_interaction_handler(name, obj)
                    elif issubclass(obj, TaskGenerator) and obj != TaskGenerator:
                        self.register_task_generator(name, obj)
                    elif issubclass(obj, Rule) and obj != Rule:
                        self.register_rule(name, obj)
        
        except ImportError as e:
            raise ImportError(f"Could not load module {module_path}: {e}")
    
    def get_available_components(self) -> Dict[str, List[str]]:
        """Get a summary of all available components."""
        return {
            "agent_types": list(self._agent_types.keys()),
            "behaviors": list(self._behaviors.keys()),
            "interaction_handlers": list(self._interaction_handlers.keys()),
            "task_generators": list(self._task_generators.keys()),
            "rules": list(self._rules.keys()),
            "components": list(self._components.keys())
        }

# Global registry instance
registry = ComponentRegistry()