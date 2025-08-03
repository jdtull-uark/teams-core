"""
Test script to verify team efficacy tracking works properly.
"""

from src.engineering.model import EngineeringTeamModel, create_engineering_config
from src.engineering.utils import register_engineering_components

# Register all components
register_engineering_components()

def test_team_efficacy_tracking():
    """Test that team efficacy is properly tracked."""
    
    # Create a small model for testing
    model = EngineeringTeamModel(
        num_engineers=3,
        num_managers=0,
        initial_tasks=5,
        num_steps=50,
        grid_size=5,
        enable_logging=True
    )
    
    print("Testing team efficacy tracking...")
    print(f"Initial model setup: {len(model.agents)} agents, {len(model.tasks)} tasks")
    
    # Check that agents have the perceived_team_efficacy attribute
    for agent in model.agents:
        if hasattr(agent, 'perceived_team_efficacy'):
            print(f"Agent {agent.unique_id}: initial team efficacy = {agent.perceived_team_efficacy:.3f}")
        else:
            print(f"ERROR: Agent {agent.unique_id} missing perceived_team_efficacy attribute!")
    
    # Run a few steps
    print("\nRunning simulation for 20 steps...")
    for step in range(20):
        model.step()
        if step % 5 == 0:
            avg_efficacy = sum(getattr(a, 'perceived_team_efficacy', 0.5) for a in model.agents) / len(model.agents)
            print(f"Step {step}: Average team efficacy = {avg_efficacy:.3f}")
            # Print individual values too
            for agent in model.agents:
                pte = getattr(agent, 'perceived_team_efficacy', 0.5)
                print(f"  Agent {agent.unique_id}: {pte:.3f}")
    
    # Check datacollector
    if hasattr(model, 'datacollector'):
        model_data = model.datacollector.get_model_vars_dataframe()
        print(f"\nData collected columns: {list(model_data.columns)}")
        
        if 'Average_Team_Efficacy' in model_data.columns:
            print("✓ Average_Team_Efficacy is being tracked!")
            print(f"Final average team efficacy: {model_data['Average_Team_Efficacy'].iloc[-1]:.3f}")
        else:
            print("✗ Average_Team_Efficacy NOT found in model data!")
            
        if 'Team_Efficacy_Std' in model_data.columns:
            print("✓ Team_Efficacy_Std is being tracked!")
        else:
            print("✗ Team_Efficacy_Std NOT found in model data!")
    else:
        print("ERROR: Model has no datacollector!")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_team_efficacy_tracking()
