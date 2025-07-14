from matplotlib.figure import Figure
import solara
from mesa.visualization import SolaraViz, make_plot_component, make_space_component
from src.model import EngineeringTeamModel
from src.agents import EngineerAgent, ManagerAgent

def agent_portrayal(agent):
    if isinstance(agent, EngineerAgent):
        return {"shape": "circle", "color": "blue", "r": 0.8}
    elif isinstance(agent, ManagerAgent):
        return {"shape": "rect", "color": "red", "w": 0.9, "h": 0.9}
    return {}

def make_knowledge_linechart(model):
    fig = Figure(figsize=(8, 5), dpi=100)
    ax = fig.subplots()

    model_data = model.datacollector.get_model_vars_dataframe()
    agent_data = model.datacollector.get_agent_vars_dataframe()

    # Retrieve agent colors based on their portrayal
    agent_colors = {
        f"Agent_{agent.unique_id}_knowledge": agent_portrayal(agent)["color"]
        for agent in model.agents
        if isinstance(agent, EngineerAgent)
    }

    for column in model_data.columns:
        if column == "Average_knowledge":
            line_color = agent_colors.get(column, "black")

            ax.plot(
                model_data.index,
                model_data[column],
                label=f"TEAM",
                color=line_color,
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

    # Retrieve agent colors based on their portrayal
    agent_colors = {
        f"Agent_{agent.unique_id}_psychSafety": agent_portrayal(agent)["color"]
        for agent in model.agents
        if isinstance(agent, EngineerAgent)
    }

    for column in model_data.columns:
        if column == "Average_PPS":
            line_color = agent_colors.get(column, "black")

            ax.plot(
                model_data.index,
                model_data[column],
                label=f"TEAM",
                color=line_color,
            )

    ax.set_title("Revenue of Each Store Over Time")
    ax.set_xlabel("Simulation Step")
    ax.set_ylabel("Revenue")

    fig.tight_layout()

    return solara.FigureMatplotlib(fig)


graph = make_space_component(agent_portrayal, backend="matplotlib")

model_params = {
    "num_engineers": {
        "type": "SliderInt",
        "value": 20,
        "label": "Number of agents:",
        "min": 2,
        "max": 100,
        "step": 1,
    },
    "num_steps": {
        "type": "SliderInt",
        "value": 1,
        "label": "Number of steps:",
        "min": 2,
        "max": 1000,
        "step": 1,
    },
}


model = EngineeringTeamModel()

page = SolaraViz(
    model,
    components=[graph, make_psych_safety_linechart, make_knowledge_linechart],
    model_params=model_params,
    name="TEAMS Model",
)