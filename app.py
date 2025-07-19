from matplotlib.figure import Figure
import solara
from mesa.visualization import SolaraViz, make_plot_component, make_space_component
from src.model import EngineeringTeamModel
from src.agents import EngineerAgent, ManagerAgent

def agent_portrayal(agent):
    if isinstance(agent, EngineerAgent):
        if agent.seeking_agent:
            return {"color": "green", "w": 0.7, "h": 0.7}
        elif agent.seeking_knowledge:
            return {"color": "orange", "w": 0.7, "h": 0.7}
        else:
            return {"color": "blue"}
    elif isinstance(agent, ManagerAgent):
        return {"color": "red", "w": 0.9, "h": 0.9}
    return {}

def make_knowledge_linechart(model):
    fig = Figure(figsize=(8, 5), dpi=100)
    ax = fig.subplots()

    model_data = model.datacollector.get_model_vars_dataframe()
    agent_data = model.datacollector.get_agent_vars_dataframe()

    for column in model_data.columns:
        if column == "Average_knowledge":
            ax.plot(
                model_data.index,
                model_data[column],
                label=f"TEAM",
                color="blue"
            )

    ax.set_title("Knowledge")
    ax.set_xlabel("Simulation Step")
    ax.set_ylabel("Knowledge")

    fig.tight_layout()

    return solara.FigureMatplotlib(fig)

def make_psych_safety_linechart(model):
    fig = Figure(figsize=(8, 5), dpi=100)
    ax = fig.subplots()

    model_data = model.datacollector.get_model_vars_dataframe()
    agent_data = model.datacollector.get_agent_vars_dataframe()

    for column in model_data.columns:
        if column == "Average_PPS":
            ax.plot(
                model_data.index,
                model_data[column],
                label=f"TEAM",
            )

    ax.set_title("Psychological Safety")
    ax.set_xlabel("Simulation Step")
    ax.set_ylabel("Psychological Safety")

    fig.tight_layout()

    return solara.FigureMatplotlib(fig)

def make_task_status_chart(model):
    """Create a chart showing current task for each agent."""
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
            task_display = 'Idle'
        else:
            task_display = f"Task {current_task}"
        
        tasks.append(task_display)
        
        # Color code by agent type
        if isinstance(agent, EngineerAgent):
            colors.append('blue')
        elif isinstance(agent, ManagerAgent):
            colors.append('red')
        else:
            colors.append('gray')
    
    # Create horizontal bar chart
    y_pos = range(len(agents))
    
    # Create bars (just for visuals - length doesn't matter much)
    bars = ax.barh(y_pos, [1] * len(agents), color=colors, alpha=0.7)
    
    # Add task text on the bars
    for i, (bar, task) in enumerate(zip(bars, tasks)):
        # Truncate long task names
        display_task = task[:30] + "..." if len(task) > 30 else task
        ax.text(0.5, bar.get_y() + bar.get_height()/2, display_task, 
                ha='center', va='center', fontweight='bold', fontsize=9)
    
    # Customize the chart
    ax.set_yticks(y_pos)
    ax.set_yticklabels(agents)
    ax.set_xlabel('Current Task')
    ax.set_title(f'Agent Task Status (Step {model.steps})')
    ax.set_xlim(0, 1)
    
    # Remove x-axis ticks since they're not meaningful
    ax.set_xticks([])
    
    # Invert y-axis to show Agent 0 at the top
    ax.invert_yaxis()
    
    # Add grid for better readability
    ax.grid(True, axis='y', alpha=0.3)
    
    fig.tight_layout()
    
    return solara.FigureMatplotlib(fig)


def make_knowledge_linechart(model):
    fig = Figure(figsize=(8, 5), dpi=100)
    ax = fig.subplots()

    model_data = model.datacollector.get_model_vars_dataframe()
    agent_data = model.datacollector.get_agent_vars_dataframe()

    for column in model_data.columns:
        if column == "Average_knowledge":

            ax.plot(
                model_data.index,
                model_data[column],
                label=f"TEAM",
                color="blue"
            )

    ax.set_title("Knowledge")
    ax.set_xlabel("Simulation Step")
    ax.set_ylabel("Knowledge")

    fig.tight_layout()

    return solara.FigureMatplotlib(fig)


def make_psych_safety_linechart(model):
    fig = Figure(figsize=(8, 5), dpi=100)
    ax = fig.subplots()

    model_data = model.datacollector.get_model_vars_dataframe()
    agent_data = model.datacollector.get_agent_vars_dataframe()

    for column in model_data.columns:
        if column == "Average_PPS":
            ax.plot(
                model_data.index,
                model_data[column],
                label=f"TEAM",
            )

    ax.set_title("Psychological Safety")
    ax.set_xlabel("Simulation Step")
    ax.set_ylabel("Psychological Safety")

    fig.tight_layout()

    return solara.FigureMatplotlib(fig)


graph = make_space_component(agent_portrayal, backend="matplotlib")

model_params = {
    "num_engineers": {
        "type": "SliderInt",
        "value": 5,
        "label": "Number of agents:",
        "min": 2,
        "max": 15,
        "step": 1,
    },
    "num_steps": {
        "type": "SliderInt",
        "value": 300,
        "label": "Number of steps:",
        "min": 2,
        "max": 1000,
        "step": 1,
    },
    "psych_safety_threshold": {
        "type": "SliderFloat",
        "value": 0.5,
        "label": "PS Threshold:",
        "min": 0,
        "max": 1,
        "step": 0.05,
    }
}


def create_model(**kwargs):
    """Factory function to create model with logging enabled."""
    
    model = EngineeringTeamModel(**kwargs, enable_logging=True)
    
    return model

page = SolaraViz(
    create_model(),
    components=[graph, make_psych_safety_linechart, make_knowledge_linechart, make_task_status_chart],
    model_params=model_params,
    name="TEAMS Model",
)