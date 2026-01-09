from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import solara
from mesa.visualization import SolaraViz, make_space_component

from examples.psych_safety_example.extended_model import PsychSafetyEngineeringModel
from examples.psych_safety_example.extended_agents import PsychSafetyEngineerAgent
from examples.psych_safety_example.rules import PsychologicalSafetyRule, ProductivityRule
from examples.psych_safety_example.interactions import PerformanceEvaluationHandler
from examples.psych_safety_example.behaviors import EvaluationBehavior

# Import core components
from src.framework.core.registry import registry

def agent_portrayal(agent):
    if isinstance(agent, PsychSafetyEngineerAgent):
        comm_manager = agent.get_component("communication_manager")
        if comm_manager and hasattr(comm_manager, 'searching_agents') and comm_manager.searching_agents:
            return {"color": "green"}
        elif comm_manager and hasattr(comm_manager, 'seeking_knowledge') and comm_manager.seeking_knowledge:
            return {"color": "orange"}
        else:
            return {"color": "blue"}
    return {"color": "gray"}

def add_legend(ax):
    """Add a legend to the visualization based on agent status present"""
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

def make_task_completion_linechart(model):
    if callable(model):
        model = model()

    fig = Figure(figsize=(8, 5), dpi=100)
    ax = fig.subplots()

    model_data = model.datacollector.get_model_vars_dataframe()

    for column in model_data.columns:
        if column == "Completed_Tasks":
            ax.plot(
                model_data.index,
                model_data[column],
                label=f"TEAM",
                color="blue"
            )

    ax.set_title("Total Tasks Completed")
    ax.set_xlabel("Simulation Step")
    ax.set_xlim(0, model.max_steps)
    ax.set_ylabel("Tasks Completed")

    fig.tight_layout()

    return solara.FigureMatplotlib(fig)

def make_knowledge_linechart(model):
    if callable(model):
        model = model()

    fig = Figure(figsize=(8, 5), dpi=100)
    ax = fig.subplots()

    model_data = model.datacollector.get_model_vars_dataframe()

    for column in model_data.columns:
        if column == "Average_Knowledge":
            ax.plot(
                model_data.index,
                model_data[column],
                label=f"TEAM",
                color="blue"
            )

    ax.set_title("Average Member Knowledge")
    ax.set_xlabel("Simulation Step")
    ax.set_xlim(0, model.max_steps)
    ax.set_ylabel("Knowledge")

    fig.tight_layout()

    return solara.FigureMatplotlib(fig)

def make_psych_safety_linechart(model):
    if callable(model):
        model = model()

    fig = Figure(figsize=(8, 5), dpi=100)
    ax = fig.subplots()

    model_data = model.datacollector.get_model_vars_dataframe()

    for column in model_data.columns:
        if column == "Average_PPS":
            ax.plot(
                model_data.index,
                model_data[column],
                label=f"TEAM",
            )

    ax.set_title("Team Psychological Safety")
    ax.set_xlim(0, model.max_steps)
    ax.set_xlabel("Simulation Step")
    ax.set_ylabel("Psychological Safety")

    fig.tight_layout()

    return solara.FigureMatplotlib(fig)

def make_team_efficacy_linechart(model):
    if callable(model):
        model = model()

    fig = Figure(figsize=(8, 5), dpi=100)
    ax = fig.subplots()

    model_data = model.datacollector.get_model_vars_dataframe()

    # Plot average team efficacy
    if "Average_Team_Efficacy" in model_data.columns:
        ax.plot(
            model_data.index,
            model_data["Average_Team_Efficacy"],
            label="Average Team Efficacy",
            color="green",
            linewidth=2
        )

    ax.set_title("Perceived Team Efficacy")
    ax.set_xlabel("Simulation Step")
    ax.set_ylabel("Team Efficacy")
    ax.set_ylim(0, 1)  # Team efficacy is bounded between 0 and 1
    ax.set_xlim(0, model.max_steps)
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.tight_layout()

    return solara.FigureMatplotlib(fig)

def make_task_status_chart(model):
    """Create a chart showing current task for each agent."""
    if callable(model):
        model = model()

    fig = Figure(figsize=(10, 8), dpi=100)
    ax = fig.subplots()

    # Get agent data from datacollector
    agent_data = model.datacollector.get_agent_vars_dataframe()
    
    # Get all agents and their current tasks
    agents = []
    tasks = []
    colors = []
    
    for agent in model.agents:
        agents.append(f"Agent {agent.unique_id}")
        
        current_task = None
        if not agent_data.empty and len(agent_data) > 0:
            try:
                latest_step = agent_data.index.get_level_values('Step').max()
                agent_row = agent_data.loc[(latest_step, agent.unique_id)]
                current_task = agent_row.get('Current_Task', None)
            except (KeyError, IndexError):
                pass
        
        # Fallback to direct attribute access
        if current_task is None:
            current_task = agent.current_task.id if hasattr(agent, "current_task") and agent.current_task else None
        
        if current_task is None:
            if agent.get_component("task_manager") and agent.get_component("task_manager").all_tasks_completed:
                task_display = 'All Tasks Completed'
            else:
                task_display = 'Idle'
        else:
            task_display = f"Task {current_task}"
        
        tasks.append(task_display)
        
        # Color code by agent type
        if isinstance(agent, PsychSafetyEngineerAgent):
            colors.append('blue')
        else:
            colors.append('gray')
    
    # Create horizontal bar chart
    y_pos = range(len(agents))
    
    # Create bars
    bars = ax.barh(y_pos, [1] * len(agents), color=colors, alpha=0.7)
    
    # Add task text on the bars
    for i, (bar, task) in enumerate(zip(bars, tasks)):
        display_task = task[:30] + "..." if len(task) > 30 else task
        ax.text(0.5, bar.get_y() + bar.get_height()/2, display_task, 
                ha='center', va='center', fontweight='bold', fontsize=9)
    
    # Customize the chart
    ax.set_yticks(y_pos)
    ax.set_yticklabels(agents)
    ax.set_xlabel('Current Task')
    ax.set_title(f'Agent Task Status (Step {model.steps})')
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.invert_yaxis()
    ax.grid(True, axis='y', alpha=0.3)
    
    fig.tight_layout()
    
    return solara.FigureMatplotlib(fig)


graph = make_space_component(
    agent_portrayal, 
    backend="matplotlib",
    post_process=add_legend
)

model_params = {
    "num_engineers": {
        "type": "SliderInt",
        "value": 5,
        "label": "Number of engineers:",
        "min": 2,
        "max": 15,
        "step": 1,
    },
    "initial_tasks": {
        "type": "SliderInt",
        "value": 10,
        "label": "Initial tasks:",
        "min": 10,
        "max": 50,
        "step": 1,
    },
    "num_steps": {
        "type": "SliderInt",
        "value": 100,
        "label": "Simulation steps:",
        "min": 10,
        "max": 1000,
        "step": 10,
    },
    "psychological_safety": {
        "type": "SliderFloat",
        "value": 0.5,
        "label": "Initial PS:",
        "min": 0,
        "max": 1,
        "step": 0.1,
    },
    "contributed_psychological_safety": {
        "type": "SliderFloat",
        "value": 0.0,
        "label": "Initial CPS:",
        "min": -1,
        "max": 1,
        "step": 0.1,
    },
    "grid_size": {
        "type": "SliderInt",
        "value": 10,
        "label": "Grid size:",
        "min": 5,
        "max": 20,
        "step": 1,
    },
}


# Register all components (core + example)
from src.engineering.utils import register_engineering_components
register_engineering_components()

# Register example-specific components
registry.register_agent_type("PsychSafetyEngineerAgent", PsychSafetyEngineerAgent)
registry.register_rule("PsychologicalSafetyRule", PsychologicalSafetyRule)
registry.register_rule("ProductivityRule", ProductivityRule)
registry.register_interaction_handler("PerformanceEvaluationHandler", PerformanceEvaluationHandler)
registry.register_behavior("EvaluationBehavior", EvaluationBehavior)

# Create model instance
model = PsychSafetyEngineeringModel(
    num_managers=0,
    enable_logging=True,
    verbose=False
)

# Create Solara visualization
page = SolaraViz(
    model,
    components=[
        graph, 
        make_task_completion_linechart, 
        make_psych_safety_linechart, 
        make_knowledge_linechart, 
        make_team_efficacy_linechart, 
        make_task_status_chart
    ],
    model_params=model_params,
    name="TEAMS Model - with Psychological Safety",
)
