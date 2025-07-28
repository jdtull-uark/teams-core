#!/usr/bin/env python3
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

    directory = os.path.dirname(os.path.abspath(__file__))
    
    # Load configuration
    config = ModelConfig.from_file(os.path.join(directory, "configs", "default.yaml"))

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
    print(f"\nSimulation completed after {model.step_count} steps")
    
    # Get final data
    final_data = model.datacollector.get_model_vars_dataframe()
    if not final_data.empty:
        print(f"Final completed tasks: {final_data['Completed_Tasks'].iloc[-1]}")
        print(f"Final psychological safety: {final_data['Psychological_Safety'].iloc[-1]:.3f}")
        print(f"Average knowledge per agent: {final_data['Average_Knowledge'].iloc[-1]:.1f}")
    
    # Save results
    model.datacollector.get_model_vars_dataframe().to_csv(os.path.join(directory, "results", "model_data.csv"))
    model.datacollector.get_agent_vars_dataframe().to_csv(os.path.join(directory, "results", "agent_data.csv"))

    print("Results saved to results/ directory")

if __name__ == "__main__":
    main()