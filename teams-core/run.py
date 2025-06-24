# Example script to run the simulation

from src.model import EngineeringTeamModel

def run_basic_simulation(steps: int = 20):
    """Run a basic simulation and return the model."""
    model = EngineeringTeamModel()
    
    print(f"Starting simulation with {model.num_engineers} engineers, {model.num_managers} managers")
    print(f"Initial tasks: {len(model.tasks)}")
    
    for i in range(steps):
        model.step()
        completed = len([t for t in model.tasks.values() if t.status.value == "completed"])
        active = len([t for t in model.tasks.values() if t.status.value == "in_progress"])
        
        if i % 5 == 0:
            print(f"Step {i}: {completed} completed, {active} active")
    
    return model

if __name__ == "__main__":
    print("Running basic engineering team simulation...")
    model = run_basic_simulation()
    
    # Final results
    df = model.datacollector.get_model_vars_dataframe()
    print(f"\nFinal results:")
    print(f"Completed tasks: {df['Completed_Tasks'].iloc[-1]}")
    print(f"Active tasks: {df['Active_Tasks'].iloc[-1]}")