from matplotlib.figure import Figure
import solara
from mesa.visualization import SolaraViz, make_plot_component, make_space_component
from src.model import EngineeringTeamModel
from src.agents import EngineerAgent, ManagerAgent

def agent_portrayal(agent):
    if isinstance(agent, EngineerAgent):
        if agent.searching_agents:
            return {"color": "green", "w": 0.7, "h": 0.7}
        elif agent.searching_agents:
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

def make_gantt_chart(model):
    fig = Figure(figsize=(12, 8), dpi=100)
    ax = fig.subplots()
    
    # Get data from datacollector
    agent_data = model.datacollector.get_agent_vars_dataframe()
    
    if agent_data.empty:
        ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
        return solara.FigureMatplotlib(fig)
    
    # Get all steps and agents
    steps = sorted(agent_data.index.get_level_values('Step').unique())
    agent_ids = sorted(agent_data.index.get_level_values('AgentID').unique())
    
    agents = []
    y_positions = []
    colors = []
    
    y_pos = 0
    
    for agent_id in agent_ids:
        agent = next((a for a in model.agents if a.unique_id == agent_id), None)
        if not agent:
            continue
            
        agents.append(f"Agent {agent_id}")
        y_positions.append(y_pos)
        
        # Color by agent type
        if isinstance(agent, EngineerAgent):
            color = 'blue'
        elif isinstance(agent, ManagerAgent):
            color = 'red'
        else:
            color = 'gray'
        colors.append(color)
        
        # Track task assignments across steps
        current_task = None
        task_start = None
        
        for step in steps:
            try:
                step_data = agent_data.loc[(step, agent_id)]
                task = step_data['Current_Task']
                task_id = task.id if task else None 
                subtask = step_data['Current_Subtask']
                subtask_id = subtask.id if subtask else None
                
                # Check if task changed
                if task != current_task:
                    # End previous task bar if exists
                    if current_task is not None:
                        task_duration = step - task.start_time
                        if task_duration > 0:
                            # Draw task bar
                            ax.barh(y_pos, task_duration, left=task.start_time, height=0.8,
                                   color=colors[y_pos], alpha=0.6, edgecolor='black', linewidth=1)
                            
                            # Add task label
                            ax.text(task.start_time + task_duration/2, y_pos, f"Task {current_task.id}",
                                   ha='center', va='center', fontweight='bold', fontsize=8)
                    
                    # Start new task
                    current_task = task
                
                if subtask:
                    subtask_duration = step - subtask.start_time if hasattr(subtask, 'start_time') else 0
                    progress = getattr(subtask, 'progress', 0.0)
                    # Draw progress indicator
                    if progress > 0:
                        ax.barh(y_pos+0.5, subtask_duration, left=step, height=0.4,
                                color=colors[y_pos], alpha=progress)
                    break
                
            except KeyError:
                # No data for this agent at this step
                continue
        
        # Handle final task if agent is still working
        if current_task is not None:
            final_step = steps[-1]
            task_duration = final_step - task.start_time + 1
            ax.barh(y_pos, task_duration, left=task.start_time, height=0.8,
                   color=colors[y_pos], alpha=0.6, edgecolor='black', linewidth=1)
            
            ax.text(task.start_time + task_duration/2, y_pos, f"Task {current_task.id}",
                   ha='center', va='center', fontweight='bold', fontsize=8)
        
        y_pos += 1
    
    # Customize the chart
    ax.set_yticks(y_positions)
    ax.set_yticklabels(agents)
    ax.set_xlabel('Simulation Step')
    ax.set_title(f'Agent Task Timeline (Current Step: {model.steps})')
    
    if steps:
        ax.set_xlim(0, max(steps) + 1)
    else:
        ax.set_xlim(0, 1)
    
    # Invert y-axis to show first agent at top
    ax.invert_yaxis()
    
    # Add grid
    ax.grid(True, axis='x', alpha=0.3)
    
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
    components=[graph, make_psych_safety_linechart, make_knowledge_linechart, make_gantt_chart],
    model_params=model_params,
    name="TEAMS Model",
)