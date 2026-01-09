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
    registry.register_agent_type("ManagerAgent", agents.ManagerAgent)
    
    # Register behaviors
    registry.register_behavior("WorkBehavior", behaviors.WorkBehavior)
    registry.register_behavior("LearnBehavior", behaviors.LearnBehavior)
    registry.register_behavior("CommunicationBehavior", behaviors.CommunicationBehavior)
    registry.register_behavior("MovementBehavior", behaviors.MovementBehavior)
    
    # Register interaction handlers
    registry.register_interaction_handler("KnowledgeShareHandler", interactions.KnowledgeShareHandler)
    registry.register_interaction_handler("HelpRequestHandler", interactions.HelpRequestHandler)
    
    # Register task generators
    registry.register_task_generator("EngineeringTaskGenerator", tasks.EngineeringTaskGenerator)
    

