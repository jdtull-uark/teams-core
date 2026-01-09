# Psychological Safety Example

This example demonstrates how to extend the core TEAMS engineering model with psychological safety and team efficacy features.

## Overview

This example shows the framework's extensibility by adding:
- **Perceived Psychological Safety (PPS)**: How safe each agent feels in the team
- **Contributed Psychological Safety (CPS)**: How much safety each agent contributes
- **Perceived Team Efficacy**: Each agent's belief in the team's capabilities
- **Performance Evaluation**: Agents evaluate each other's performance
- **Productivity Rules**: Performance influenced by psychological safety

## Architecture

The example follows a clean extension pattern:

### Extended Components

1. **`extended_agents.py`**: `PsychSafetyEngineerAgent` extends `EngineerAgent` with three new attributes
2. **`extended_model.py`**: `PsychSafetyEngineeringModel` extends `EngineeringTeamModel` with initialization logic
3. **`rules.py`**: Domain-specific rules for psychological safety dynamics
4. **`interactions.py`**: Performance evaluation interaction handler
5. **`behaviors.py`**: Evaluation behavior for agents

### How It Works

The extended model:
1. Calls the parent `EngineeringTeamModel` constructor (core functionality)
2. Adds psychological safety initialization after agents are created
3. Registers extended components with the framework
4. All core knowledge sharing and task completion mechanics remain intact

## Running the Example

### Option 1: Run with Solara (Visualization)

From the repository root:

```bash
# Run the example app
solara run examples/psych_safety_example/app.py --host localhost --port 8765
```

Then open your browser to `http://localhost:8765`

### Option 2: Run as Script

```python
from examples.psych_safety_example import PsychSafetyEngineeringModel

# Create and run model
model = PsychSafetyEngineeringModel(
    num_engineers=5,
    initial_tasks=10,
    num_steps=100,
    psychological_safety=0.5,
    contributed_psychological_safety=0.0,
    verbose=True
)

# Run simulation
for i in range(model.config.num_steps):
    model.step()

# Analyze results
model_data = model.datacollector.get_model_vars_dataframe()
print(model_data.head())
```

## Key Features

### Psychological Safety Dynamics

- **PPS Updates**: Agents' perceived safety adjusts based on interactions with teammates
- **CPS Influence**: Agents with higher contributed safety improve their teammates' perceptions
- **Knowledge Sharing**: Willingness to share knowledge influenced by psychological safety
- **Productivity Impact**: Work efficiency affected by psychological safety levels

### Team Efficacy

- **Performance-Based**: Agents update their team efficacy beliefs based on observed task performance
- **Peer Evaluation**: Agents evaluate nearby teammates and update their efficacy perceptions
- **Exceptional Performance Rewards**: Faster-than-expected task completion boosts team efficacy

## Visualizations

The example app provides:

1. **Space View**: Agent positions and states (searching, working, idle)
2. **Task Completion**: Total completed tasks over time
3. **Psychological Safety**: Average PPS across the team
4. **Knowledge Growth**: Average knowledge per agent
5. **Team Efficacy**: How team confidence evolves
6. **Task Status**: Current task assignments per agent

## Extending Further

You can build on this example:

```python
from examples.psych_safety_example import PsychSafetyEngineerAgent

class MyCustomAgent(PsychSafetyEngineerAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.my_new_attribute = 0.5
```

Or create your own rules:

```python
from src.framework.core.interfaces import Rule

class MyCustomRule(Rule):
    def should_apply(self, model) -> bool:
        return model.step_count % 5 == 0
    
    def apply(self, model) -> None:
        # Your custom logic here
        pass
```

## Comparison with Core Model

| Feature | Core Model | This Example |
|---------|-----------|--------------|
| Knowledge Sharing | ✅ | ✅ |
| Task Completion | ✅ | ✅ |
| Movement/Collaboration | ✅ | ✅ |
| Psychological Safety | ❌ | ✅ |
| Team Efficacy | ❌ | ✅ |
| Performance Evaluation | ❌ | ✅ |

## Files

- `extended_agents.py` - Agent with psych safety attributes
- `extended_model.py` - Model with psych safety initialization
- `rules.py` - PsychologicalSafetyRule & ProductivityRule
- `interactions.py` - PerformanceEvaluationHandler
- `behaviors.py` - EvaluationBehavior
- `app.py` - Solara visualization app
- `README.md` - This file
- `__init__.py` - Package exports

## Research Context

This example is based on research in organizational psychology:

- **Psychological Safety**: Edmondson (1999) - team learning and performance
- **Team Efficacy**: Bandura (1997) - collective efficacy beliefs
- **Performance Feedback**: DeNisi & Kluger (2000) - feedback intervention theory

## License

Same as the main TEAMS project.
