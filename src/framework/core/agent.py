"""
Base agent class with pluggable behavior system.
"""

import mesa
import random
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..core.interfaces import AgentBehavior, Component

if TYPE_CHECKING:
    from .model import BaseModel

class BaseAgent(mesa.Agent):
    """
    Base agent class with support for pluggable behaviors and components.
    """
    
    def __init__(self, unique_id: int, model: 'BaseModel'):
        super().__init__(model)
        self.name = f"Agent {unique_id}"
        self.attributes: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []
        
        # Behavior system
        self.behaviors: List[AgentBehavior] = []
        self.components: Dict[str, Component] = {}
        
        # State tracking
        self.active = True
        self.position = None
    
    def add_behavior(self, behavior: AgentBehavior) -> None:
        """Add a behavior to this agent."""
        if behavior not in self.behaviors:
            self.behaviors.append(behavior)
    
    def remove_behavior(self, behavior: AgentBehavior) -> None:
        """Remove a behavior from this agent."""
        if behavior in self.behaviors:
            self.behaviors.remove(behavior)
    
    def add_component(self, name: str, component: Component) -> None:
        """Add a component to this agent with validation."""
        if not name.isidentifier():
            raise ValueError(f"Invalid component name: {name}")
        if name in self.components:
            raise ValueError(f"Component already exists: {name}")
        self.components[name] = component
        component.initialize(self)
    
    def get_component(self, name: str) -> Optional[Component]:
        """Get a component by name."""
        return self.components.get(name)

    def remove_component(self, name: str) -> None:
        """Remove and clean up a component."""
        if name in self.components:
            if hasattr(self.components[name], 'cleanup'):
                self.components[name].cleanup()
            del self.components[name]

    def log_action(self, action: str, details: Dict[str, Any] = None) -> None:
        """Log an action taken by the agent."""
        log_entry = {
            "step": self.model.steps,
            "agent_id": self.unique_id,
            "action": action,
            "details": details or {}
        }
        self.history.append(log_entry)
        
        # Also log to model's logging system if available
        if hasattr(self.model, 'log_agent_action'):
            self.model.log_agent_action(self.unique_id, action, details)
    
    def interact_with(self, other_agent: 'BaseAgent', interaction_type: str, 
                     context: Dict[str, Any] = None) -> bool:
        """Initiate an interaction with another agent."""
        if not context:
            context = {}
        
        context.update({
            "initiator": self,
            "recipient": other_agent,
            "step": self.model.steps
        })
        
        # Use model's interaction system
        return self.model.handle_interaction(self, other_agent, interaction_type, context)
    
    def step(self) -> None:
        """Execute one simulation step."""
        if not self.active:
            return
        
        try:
            # Execute all behaviors
            for behavior in self.behaviors:
                try:
                    if behavior.can_execute(self, self.model):
                        behavior.execute(self, self.model)
                except Exception as e:
                    self.log_action("behavior_error", {
                        "behavior": type(behavior).__name__,
                        "error": str(e)
                    })
        except Exception as e:
            self.log_action("step_error", {"error": str(e)})
            raise 
                
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the agent for serialization/debugging."""
        return {
            "unique_id": self.unique_id,
            "name": self.name,
            "active": self.active,
            "position": self.position,
            "attributes": self.attributes.copy(),
            "behaviors": [type(b).__name__ for b in self.behaviors],
            "components": list(self.components.keys())
        }

    def clear_history(self, before_step: Optional[int] = None) -> None:
        """Clear agent history, optionally before a specific step."""
        if before_step is not None:
            self.history = [entry for entry in self.history 
                        if entry["step"] >= before_step]
        else:
            self.history.clear()
    
    def soft_reset_components(self) -> None:
        """Perform a soft reset on all components."""
        for component in self.components.values():
            component.soft_reset()
    
    def close_components(self) -> None:
        """Close/finalize all components."""
        for component in self.components.values():
            component.close()

    def reset_state(self) -> None:
        """Reset agent to initial state."""
        self.attributes.clear()
        self.history.clear()
        self.active = True
        
        # Reset components
        for component in self.components.values():
            if hasattr(component, 'reset'):
                component.reset()