import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from src.engineering.model import EngineeringTeamModel
from src.engineering.agents import EngineerAgent
from src.engineering.utils import register_engineering_components

def agent_portrayal(agent):
    """Same portrayal function as your SolaraViz"""
    if isinstance(agent, EngineerAgent):
        comm_manager = agent.get_component("communication_manager")
        if comm_manager and hasattr(comm_manager, 'searching_agents') and comm_manager.searching_agents:
            return {"color": "green", "size": 50}
        elif comm_manager and hasattr(comm_manager, 'seeking_knowledge') and comm_manager.seeking_knowledge:
            return {"color": "orange", "size": 50}
        else:
            return {"color": "blue", "size": 50}
    return {"color": "gray", "size": 50}

def add_legend(ax):
    """Same legend function as your SolaraViz"""
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green',
                  markersize=8, label='Searching for Agent'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange',
                  markersize=8, label='Needs Knowledge'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue',
                  markersize=8, label='Working'),
    ]
    
    ax.legend(handles=legend_elements, loc='upper right')
    return ax

def create_engineering_model_gif(
    num_engineers=5,
    initial_tasks=10,
    grid_size=10,
    psychological_safety=0.5,
    contributed_psychological_safety=0.0,
    steps=100,
    filename='engineering_team_simulation.gif',
    fps=2
):
    """
    Create a GIF animation of your engineering team model
    
    Parameters match your SolaraViz model_params
    """
    
    # Register components (same as your SolaraViz setup)
    register_engineering_components()
    
    # Create model with same parameters as SolaraViz
    model = EngineeringTeamModel(
        num_engineers=num_engineers,
        initial_tasks=initial_tasks,
        grid_size=grid_size,
        psychological_safety=psychological_safety,
        contributed_psychological_safety=contributed_psychological_safety,
        num_managers=0,
        enable_logging=True,
        verbose=False
    )
    
    print(f"Running model for {steps} steps...")
    
    # Collect agent data for each step
    step_data = []
    for step in range(steps):
        # Collect agent positions and states
        agents_info = []
        for agent in model.agents:
            if hasattr(agent, 'pos') and agent.pos is not None:
                portrayal = agent_portrayal(agent)
                agents_info.append({
                    'x': agent.pos[0],
                    'y': agent.pos[1],
                    'color': portrayal.get('color', 'gray'),
                    'size': portrayal.get('size', 100),
                    'agent_id': agent.unique_id
                })
        
        step_data.append({
            'agents': agents_info,
            'step': step,
            'model_state': {
                'avg_knowledge': getattr(model, 'avg_knowledge', 0),
                'avg_pps': getattr(model, 'avg_pps', 0)
            }
        })
        
        # Step the model
        model.step()
        
        if step % 10 == 0:
            print(f"Completed step {step}")
    
    print("Creating animation...")
    
    # Create the animation
    fig, ax = plt.subplots(figsize=(10, 8))
    
    def animate(frame_num):
        ax.clear()
        
        frame_data = step_data[frame_num]
        agents = frame_data['agents']
        
        # Plot agents
        if agents:
            x_coords = [agent['x'] for agent in agents]
            y_coords = [agent['y'] for agent in agents]
            colors = [agent['color'] for agent in agents]
            sizes = [agent['size'] for agent in agents]
            
            scatter = ax.scatter(x_coords, y_coords, c=colors, s=sizes, alpha=0.8, edgecolors='black', linewidth=0.5)
        
        # Set grid limits
        ax.set_xlim(-0.5, grid_size - 0.5)
        ax.set_ylim(-0.5, grid_size - 0.5)
        
        # Add legend
        add_legend(ax)
        
        # Add title with step info
        ax.set_title(f'Engineering Team Simulation - Step {frame_data["step"]}', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        # Add step counter in corner
        ax.text(0.02, 0.98, f'Step: {frame_data["step"]}', 
               transform=ax.transAxes, fontsize=12, 
               verticalalignment='top', 
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Create and save animation
    ani = animation.FuncAnimation(fig, animate, frames=len(step_data),
                                interval=1000//fps, repeat=True, blit=False)
    
    print(f"Saving GIF as {filename}...")
    ani.save(filename, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"GIF saved successfully as {filename}")
    return filename

def create_metrics_gif(
    num_engineers=5,
    initial_tasks=10,
    grid_size=10,
    psychological_safety=0.5,
    contributed_psychological_safety=0.0,
    steps=100,
    filename='metrics_animation.gif',
    fps=2
):
    """Create animated GIF of the metrics charts"""
    
    register_engineering_components()
    
    model = EngineeringTeamModel(
        num_engineers=num_engineers,
        initial_tasks=initial_tasks,
        grid_size=grid_size,
        psychological_safety=psychological_safety,
        contributed_psychological_safety=contributed_psychological_safety,
        num_managers=0,
        enable_logging=True,
        verbose=False
    )
    
    print(f"Running model for metrics collection over {steps} steps...")
    
    # Run model and collect data
    for step in range(steps):
        model.step()
        if step % 10 == 0:
            print(f"Completed step {step}")
    
    # Get the collected data
    model_data = model.datacollector.get_model_vars_dataframe()
    
    print("Creating metrics animation...")
    
    # Create subplots for all metrics
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Engineering Team Metrics Over Time', fontsize=16, fontweight='bold')
    
    def animate_metrics(frame_num):
        # Clear all axes
        for ax in [ax1, ax2, ax3, ax4]:
            ax.clear()
        
        # Current step data (up to current frame)
        current_data = model_data.iloc[:frame_num+1] if frame_num > 0 else model_data.iloc[:1]
        
        # Plot 1: Average Knowledge
        if "Average_Knowledge" in current_data.columns:
            ax1.plot(current_data.index, current_data["Average_Knowledge"], 
                    color="blue", linewidth=2, marker='o', markersize=3)
            ax1.set_title("Average Member Knowledge", fontsize=12, fontweight='bold')
            ax1.set_xlabel("Simulation Step")
            ax1.set_ylabel("Knowledge")
            ax1.grid(True, alpha=0.3)
            ax1.set_xlim(0, len(model_data))
            if len(current_data) > 0:
                ax1.set_ylim(0, model_data["Average_Knowledge"].max() * 1.1)
        
        # Plot 2: Psychological Safety
        if "Average_PPS" in current_data.columns:
            ax2.plot(current_data.index, current_data["Average_PPS"], 
                    color="green", linewidth=2, marker='s', markersize=3)
            ax2.set_title("Team Psychological Safety", fontsize=12, fontweight='bold')
            ax2.set_xlabel("Simulation Step")
            ax2.set_ylabel("Psychological Safety")
            ax2.grid(True, alpha=0.3)
            ax2.set_xlim(0, len(model_data))
            if len(current_data) > 0:
                y_min = min(0, model_data["Average_PPS"].min() * 1.1)
                y_max = model_data["Average_PPS"].max() * 1.1
                ax2.set_ylim(y_min, y_max)
        
        # Plot 3: Team Efficacy
        if "Average_Team_Efficacy" in current_data.columns:
            ax3.plot(current_data.index, current_data["Average_Team_Efficacy"], 
                    color="red", linewidth=2, marker='^', markersize=3)
            ax3.set_title("Perceived Team Efficacy", fontsize=12, fontweight='bold')
            ax3.set_xlabel("Simulation Step")
            ax3.set_ylabel("Team Efficacy")
            ax3.set_ylim(0, 1)
            ax3.grid(True, alpha=0.3)
            ax3.set_xlim(0, len(model_data))
        
        # Plot 4: Task Completion (if available) or other metric
        if "Completed_Tasks" in current_data.columns:
            ax4.plot(current_data.index, current_data["Completed_Tasks"], 
                    color="purple", linewidth=2, marker='d', markersize=3)
            ax4.set_title("Completed Tasks", fontsize=12, fontweight='bold')
            ax4.set_xlabel("Simulation Step")
            ax4.set_ylabel("Tasks Completed")
            ax4.grid(True, alpha=0.3)
            ax4.set_xlim(0, len(model_data))
            if len(current_data) > 0:
                ax4.set_ylim(0, model_data["Completed_Tasks"].max() * 1.1)
        else:
            # Alternative: show current step info
            ax4.text(0.5, 0.5, f'Current Step: {frame_num}\nTotal Steps: {len(model_data)}', 
                    transform=ax4.transAxes, fontsize=16, ha='center', va='center',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
            ax4.set_title("Simulation Progress", fontsize=12, fontweight='bold')
            ax4.set_xlim(0, 1)
            ax4.set_ylim(0, 1)
    
    # Create animation
    ani = animation.FuncAnimation(fig, animate_metrics, frames=len(model_data),
                                interval=1000//fps, repeat=True, blit=False)
    
    print(f"Saving metrics GIF as {filename}...")
    ani.save(filename, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"Metrics GIF saved successfully as {filename}")
    return filename

def create_combined_gif(
    num_engineers=5,
    initial_tasks=10,
    grid_size=10,
    psychological_safety=0.5,
    contributed_psychological_safety=0.0,
    steps=100,
    filename='combined_animation.gif',
    fps=2
):
    """Create a combined GIF with both agent visualization and metrics"""
    
    register_engineering_components()
    
    model = EngineeringTeamModel(
        num_engineers=num_engineers,
        initial_tasks=initial_tasks,
        grid_size=grid_size,
        psychological_safety=psychological_safety,
        contributed_psychological_safety=contributed_psychological_safety,
        num_managers=0,
        enable_logging=True,
        verbose=False
    )
    
    print(f"Running combined model for {steps} steps...")
    
    # Collect both agent and model data
    step_data = []
    for step in range(steps):
        # Collect agent positions
        agents_info = []
        for agent in model.agents:
            if hasattr(agent, 'pos') and agent.pos is not None:
                portrayal = agent_portrayal(agent)
                agents_info.append({
                    'x': agent.pos[0],
                    'y': agent.pos[1],
                    'color': portrayal.get('color', 'gray'),
                    'size': portrayal.get('size', 100),
                    'agent_id': agent.unique_id
                })
        
        step_data.append({
            'agents': agents_info,
            'step': step
        })
        
        model.step()
        
        if step % 10 == 0:
            print(f"Completed step {step}")
    
    # Get model data
    model_data = model.datacollector.get_model_vars_dataframe()
    
    print("Creating combined animation...")
    
    # Create figure with space visualization on left and metrics on right
    fig = plt.figure(figsize=(16, 8))
    
    # Agent space subplot
    ax_space = plt.subplot(1, 2, 1)
    
    # Metrics subplot
    ax_metrics = plt.subplot(1, 2, 2)
    
    def animate_combined(frame_num):
        ax_space.clear()
        ax_metrics.clear()
        
        frame_data = step_data[frame_num]
        agents = frame_data['agents']
        
        # Plot agents (left side)
        if agents:
            x_coords = [agent['x'] for agent in agents]
            y_coords = [agent['y'] for agent in agents]
            colors = [agent['color'] for agent in agents]
            sizes = [agent['size'] for agent in agents]
            
            ax_space.scatter(x_coords, y_coords, c=colors, s=sizes, 
                           alpha=0.8, edgecolors='black', linewidth=0.5)
        
        ax_space.set_xlim(-0.5, grid_size - 0.5)
        ax_space.set_ylim(-0.5, grid_size - 0.5)
        add_legend(ax_space)
        ax_space.set_title(f'Agent Positions - Step {frame_num}', fontsize=12, fontweight='bold')
        ax_space.grid(True, alpha=0.3)
        ax_space.set_aspect('equal')
        
        # Plot metrics up to current frame (right side)
        current_data = model_data.iloc[:frame_num+1] if frame_num > 0 else model_data.iloc[:1]
        
        if "Average_Knowledge" in current_data.columns:
            ax_metrics.plot(current_data.index, current_data["Average_Knowledge"], 
                          label="Knowledge", color="blue", linewidth=2, marker='o', markersize=2)
        
        if "Average_PPS" in current_data.columns:
            ax_metrics.plot(current_data.index, current_data["Average_PPS"], 
                          label="Psychological Safety", color="green", linewidth=2, marker='s', markersize=2)
        
        if "Average_Team_Efficacy" in current_data.columns:
            ax_metrics.plot(current_data.index, current_data["Average_Team_Efficacy"], 
                          label="Team Efficacy", color="red", linewidth=2, marker='^', markersize=2)
        
        ax_metrics.set_title(f'Team Metrics - Step {frame_num}', fontsize=12, fontweight='bold')
        ax_metrics.set_xlabel("Simulation Step")
        ax_metrics.set_ylabel("Metric Value")
        ax_metrics.legend(loc='upper left')
        ax_metrics.grid(True, alpha=0.3)
        ax_metrics.set_xlim(0, len(model_data))
        
        # Set y limits based on data range
        if len(current_data) > 0:
            all_values = []
            for col in ["Average_Knowledge", "Average_PPS", "Average_Team_Efficacy"]:
                if col in model_data.columns:
                    all_values.extend(model_data[col].values)
            if all_values:
                ax_metrics.set_ylim(min(all_values) * 0.9, max(all_values) * 1.1)
    
    plt.tight_layout()
    
    ani = animation.FuncAnimation(fig, animate_combined, frames=len(step_data),
                                interval=1000//fps, repeat=True, blit=False)
    
    print(f"Saving combined GIF as {filename}...")
    ani.save(filename, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"Combined GIF saved successfully as {filename}")
    return filename

def create_gif_with_default_params():
    """Create GIF with the same default parameters as your SolaraViz"""
    return create_engineering_model_gif(
        num_engineers=5,
        initial_tasks=10,
        grid_size=10,
        psychological_safety=0.5,
        contributed_psychological_safety=0.0,
        steps=100,
        filename='engineering_team_default.gif',
        fps=5
    )

def create_gif_with_custom_params(**kwargs):
    """Create GIF with custom parameters"""
    default_params = {
        'num_engineers': 5,
        'initial_tasks': 10,
        'grid_size': 10,
        'psychological_safety': 0.5,
        'contributed_psychological_safety': 0.0,
        'steps': 100,
        'filename': 'engineering_team_custom.gif',
        'fps': 5
    }
    
    # Update defaults with any provided kwargs
    default_params.update(kwargs)
    
    return create_engineering_model_gif(**default_params)

def create_all_gifs(
    num_engineers=5,
    initial_tasks=10,
    grid_size=10,
    psychological_safety=0.5,
    contributed_psychological_safety=0.0,
    steps=100,
    fps=2
):
    """Create all three types of GIFs with the same parameters"""
    
    print("Creating all GIF types...")
    
    # Create agent movement GIF
    print("\n1. Creating agent movement GIF...")
    create_engineering_model_gif(
        num_engineers=num_engineers,
        initial_tasks=initial_tasks,
        grid_size=grid_size,
        psychological_safety=psychological_safety,
        contributed_psychological_safety=contributed_psychological_safety,
        steps=steps,
        filename='agent_movement.gif',
        fps=fps
    )
    
    # Create metrics GIF
    print("\n2. Creating metrics GIF...")
    create_metrics_gif(
        num_engineers=num_engineers,
        initial_tasks=initial_tasks,
        grid_size=grid_size,
        psychological_safety=psychological_safety,
        contributed_psychological_safety=contributed_psychological_safety,
        steps=steps,
        filename='metrics_evolution.gif',
        fps=fps
    )
    
    # Create combined GIF
    print("\n3. Creating combined GIF...")
    create_combined_gif(
        num_engineers=num_engineers,
        initial_tasks=initial_tasks,
        grid_size=grid_size,
        psychological_safety=psychological_safety,
        contributed_psychological_safety=contributed_psychological_safety,
        steps=steps,
        filename='combined_simulation.gif',
        fps=fps
    )
    
    print("\nAll GIFs created successfully!")
    print("Files created:")
    print("- agent_movement.gif (agent positions over time)")
    print("- metrics_evolution.gif (team metrics over time)")
    print("- combined_simulation.gif (agents + metrics side by side)")

if __name__ == "__main__":
    # Example usage:
    
    # Option 1: Create all three GIF types
    create_all_gifs(
        num_engineers=5,
        initial_tasks=10,
        steps=50,  # Shorter for faster generation
        fps=3
    )
    
    # Option 2: Create individual GIFs
    # create_engineering_model_gif(filename='agents_only.gif')
    # create_metrics_gif(filename='metrics_only.gif') 
    # create_combined_gif(filename='side_by_side.gif')