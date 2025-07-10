import matplotlib.pyplot as plt # Import for displaying plots
from src.model import EngineeringTeamModel
from src.utils.analysis import analyze_results
from src.types import TaskStatus

if __name__ == "__main__":
    print("Starting Engineering Team Simulation...")

    # Define model parameters
    num_engineers = 5
    num_managers = 1
    initial_tasks = 15
    initial_psych_safety = 0.5
    psych_safety_threshold = 0.7
    num_steps = 200 # Number of simulation steps

    # Instantiate the model
    model = EngineeringTeamModel(
        num_engineers=num_engineers,
        num_managers=num_managers,
        initial_tasks=initial_tasks,
        initial_psych_safety=initial_psych_safety,
        psych_safety_threshold=psych_safety_threshold
    )

    print(f"Model initialized with {num_engineers} engineers, {num_managers} managers.")
    print(f"Initial tasks: {len(model.tasks)}. Initial Psych Safety: {model.psychological_safety:.2f}")

    # Run the model for the specified number of steps
    for i in range(num_steps):
        model.step()
        # Optional: Print progress
        if (i + 1) % 20 == 0 or i == num_steps - 1:
            completed = len([t for t in model.tasks.values() if t.status == TaskStatus.COMPLETED])
            print(f"Step {i+1}/{num_steps} | Completed Tasks: {completed} | Psych Safety: {model.psychological_safety:.2f}")
            
    print("\nSimulation Finished.")

    # Analyze and visualize results
    analyze_results(model)

    # Keep plots open until user closes them
    plt.show()