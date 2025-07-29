#!/usr/bin/env python3
'''
Example script for running an engineering team simulation using from_params method.
'''

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engineering.model import EngineeringTeamModel
from src.engineering.utils import register_engineering_components

def main():
    # Register all engineering components
    register_engineering_components()

    directory = os.path.dirname(os.path.abspath(__file__))
    
    # Create model using parameter-based constructor
    model = EngineeringTeamModel(
        num_engineers=8,
        num_managers=0,  # No managers for this simulation
        initial_tasks=15,
        num_steps=200,
        psychological_safety=0.6,
        psychological_safety_threshold=0.75,
        grid_size=15,
        enable_logging=True
    )
    
    print(f"Starting simulation with {len(model.agents)} agents...")
    print(f"Initial tasks: {len(model.tasks)}")
    print(f"Knowledge space size: {len(model.knowledge_space)}")
    print(f"Grid size: {model.space.width}x{model.space.height}")
    
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
    
    # Ensure results directory exists
    results_dir = os.path.join(directory, "results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Save results
    model.datacollector.get_model_vars_dataframe().to_csv(os.path.join(results_dir, "model_data_params.csv"))
    model.datacollector.get_agent_vars_dataframe().to_csv(os.path.join(results_dir, "agent_data_params.csv"))

    print("Results saved to results/ directory")

if __name__ == "__main__":
    main()
