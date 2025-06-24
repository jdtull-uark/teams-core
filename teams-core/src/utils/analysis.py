import numpy as np
from ..model import EngineeringTeamModel

def analyze_results(model: EngineeringTeamModel):
    """Analyze and print simulation results."""
    df = model.datacollector.get_model_vars_dataframe()
    
    print("\n=== SIMULATION RESULTS ===")
    print(f"Total steps: {len(df)}")
    print(f"Final completed tasks: {df['Completed_Tasks'].iloc[-1]}")
    