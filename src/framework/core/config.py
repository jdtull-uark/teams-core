"""
Configuration system for the framework.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import yaml
import json
from pathlib import Path

@dataclass
class ModelConfig:
    """Base configuration for model setup."""
    
    # Basic model parameters
    num_steps: int = 100
    grid_width: int = 10
    grid_height: int = 10
    grid_torus: bool = False
    random_seed: Optional[int] = None
    
    # Agent configuration
    agents: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Component configuration
    behaviors: List[Dict[str, Any]] = field(default_factory=list)
    interaction_handlers: List[Dict[str, Any]] = field(default_factory=list)
    task_generators: List[Dict[str, Any]] = field(default_factory=list)
    rules: List[Dict[str, Any]] = field(default_factory=list)
    
    # Data collection
    model_reporters: Dict[str, str] = field(default_factory=dict)
    agent_reporters: Dict[str, str] = field(default_factory=dict)
    
    # Logging
    enable_logging: bool = True
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    @classmethod
    def from_file(cls, config_path: str) -> 'ModelConfig':
        """Load configuration from a file (YAML or JSON)."""
        paths_to_try = [
            Path(config_path),
            Path.cwd() / config_path,
            Path(__file__).parent.parent.parent / config_path
        ]

        for path in paths_to_try:
                if path.exists():
                    with open(path, 'r') as f:
                        if path.suffix.lower() in ['.yaml', '.yml']:
                            data = yaml.safe_load(f)
                        elif path.suffix.lower() == '.json':
                            data = json.load(f)
                        else:
                            continue
                        return cls(**data)
                        
        raise FileNotFoundError(f"Configuration file not found at any of: {[str(p) for p in paths_to_try]}")
            
    def to_file(self, config_path: str) -> None:
        """Save configuration to a file."""
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            if path.suffix.lower() in ['.yaml', '.yml']:
                yaml.dump(self.__dict__, f, default_flow_style=False)
            elif path.suffix.lower() == '.json':
                json.dump(self.__dict__, f, indent=2)
            else:
                raise ValueError(f"Unsupported configuration file format: {path.suffix}")
