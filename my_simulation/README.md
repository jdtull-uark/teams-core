# My_Simulation

An engineering team simulation built with the agent-based modeling framework.

## Getting Started

1. Install dependencies:
   ```bash
   pip install mesa pyyaml
   ```

2. Run the simulation:
   ```bash
   python run_simulation.py
   ```

3. View results in the `results/` directory and logs in `logs/`

## Customization

- Modify `configs/default.yaml` to change simulation parameters
- Add custom agents in `custom_agents/`
- Add custom behaviors in `custom_behaviors/`
- Check `logs/` for detailed simulation logs

## Directory Structure

- `configs/` - Configuration files
- `custom_agents/` - Custom agent implementations  
- `custom_behaviors/` - Custom behavior implementations
- `results/` - Simulation output data
- `logs/` - Detailed simulation logs