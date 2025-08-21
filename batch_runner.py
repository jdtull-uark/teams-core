"""
Mesa BatchRunner implementation for TEAMS Core Engineering Simulation.

This module provides a comprehensive batch runner that can execute multiple
simulation runs with different parameter combinations, collecting and analyzing
the results across all runs.
"""

import os
import sys
import time
import pandas as pd
import random
import numpy as np
from typing import Dict, List, Any, Tuple
from pathlib import Path
from mesa.batchrunner import batch_run
from datetime import datetime
import json
import threading

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.engineering.model import EngineeringTeamModel
from src.engineering.utils import register_engineering_components


class TeamsBatchRunner:
    """
    Advanced batch runner for TEAMS engineering simulations with comprehensive
    data collection and analysis capabilities.
    """
    
    def __init__(self, 
                 output_dir: str = "batch_results",
                 max_steps: int = 500,
                 iterations_per_combination: int = 10,
                 show_progress: bool = True,
                 random_seed: int = None):
        """
        Initialize the batch runner.
        
        Args:
            output_dir: Directory to save results
            max_steps: Maximum steps per simulation run
            iterations_per_combination: Number of iterations per parameter combination
            show_progress: Whether to show progress indicators
            random_seed: Seed for reproducible results (same seed used for all runs)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.max_steps = max_steps
        self.iterations_per_combination = iterations_per_combination
        self.show_progress = show_progress
        self.random_seed = random_seed
        
        # Progress tracking
        self.total_runs = 0
        self.completed_runs = 0
        self.start_time = None
        self.progress_lock = threading.Lock()
        
        # Register all engineering components
        register_engineering_components()
        
        # Define the parameter space for batch runs
        self.variable_parameters = {
            "num_engineers": [4, 6, 8, 10],
            "initial_tasks": [8, 12, 16, 20],
            "psychological_safety": [0.3, 0.5, 0.7, 0.9],
            "grid_size": [8, 12, 16]
        }
        
        # Fixed parameters that don't vary
        self.fixed_parameters = {
            "num_managers": 0,
            "num_steps": max_steps,
            "enable_logging": False,
            "verbose": False,
        }
        
    def _update_progress(self, increment: int = 1):
        """Update progress counter and display progress."""
        if not self.show_progress:
            return
            
        with self.progress_lock:
            self.completed_runs += increment
            
            if self.total_runs > 0 and self.start_time:
                # Calculate progress
                progress_pct = (self.completed_runs / self.total_runs) * 100
                elapsed_time = time.time() - self.start_time
                
                if self.completed_runs > 0:
                    avg_time_per_run = elapsed_time / self.completed_runs
                    remaining_runs = self.total_runs - self.completed_runs
                    estimated_remaining = avg_time_per_run * remaining_runs
                    
                    # Format time displays
                    elapsed_str = self._format_time(elapsed_time)
                    remaining_str = self._format_time(estimated_remaining)
                    
                    # Create progress bar
                    bar_length = 40
                    filled_length = int(bar_length * progress_pct / 100)
                    bar = '█' * filled_length + '░' * (bar_length - filled_length)
                    
                    print(f"\r[{bar}] {progress_pct:5.1f}% | {self.completed_runs:4d}/{self.total_runs} runs | "
                          f"Elapsed: {elapsed_str} | Remaining: {remaining_str}", end='', flush=True)
                    
                    # New line when complete
                    if self.completed_runs >= self.total_runs:
                        print()
    
    def _format_time(self, seconds: float) -> str:
        """Format time in a readable format."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.0f}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def _count_combinations(self) -> int:
        """Count the total number of parameter combinations."""
        count = 1
        for param_values in self.variable_parameters.values():
            count *= len(param_values)
        return count
        
    def run_batch(self, save_intermediate: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Run the batch simulation with all parameter combinations.
        
        Args:
            save_intermediate: Whether to save intermediate results during execution
            
        Returns:
            Tuple of (model_data, agent_data) DataFrames
        """
        print("=" * 60)
        print("TEAMS CORE BATCH RUNNER")
        print("=" * 60)
        
        # Calculate total runs for progress tracking
        self.total_runs = self._count_combinations() * self.iterations_per_combination
        self.completed_runs = 0
        self.start_time = time.time()
        
        print(f"Parameter combinations to test: {self._count_combinations()}")
        print(f"Iterations per combination: {self.iterations_per_combination}")
        print(f"Total simulation runs: {self.total_runs}")
        print(f"Maximum steps per run: {self.max_steps}")
        print(f"Output directory: {self.output_dir}")
        print("=" * 60)
        
        if self.show_progress:
            print("Starting batch execution...")
            print()  # Extra line for progress bar
        
        # Combine variable and fixed parameters for Mesa's batch_run
        parameters = {}
        
        # Add variable parameters (these will be varied)
        for param, values in self.variable_parameters.items():
            parameters[param] = values
        
        # Add fixed parameters (these will stay constant)
        for param, value in self.fixed_parameters.items():
            parameters[param] = value

        parameters['print_progress_bar'] = False

        # Use Mesa's batch_run function with progress tracking
        results = batch_run(
            model_cls=EngineeringTeamModel,
            parameters=parameters,
            iterations=self.iterations_per_combination,
            number_processes=2,
            max_steps=self.max_steps,
            number_processes=1,
            data_collection_period=1,
            display_progress=True
        )
        
        if self.show_progress:
            print("Batch execution completed!")
        
        # Convert results to DataFrames
        model_data = pd.DataFrame(results)
        
        # The agent data is embedded in the model data, we need to extract it
        agent_data = self._extract_agent_data(results)
        
        # Add timestamp and run metadata
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_data['timestamp'] = timestamp
        if agent_data is not None:
            agent_data['timestamp'] = timestamp
        
        # Calculate execution time
        execution_time = time.time() - self.start_time
        print(f"\nTotal execution time: {execution_time:.2f} seconds")
        print(f"Average time per run: {execution_time / self.total_runs:.2f} seconds")
        
        # Save results
        if save_intermediate:
            self.save_results(model_data, agent_data, timestamp)
        
        return model_data, agent_data
    
    def _extract_agent_data(self, results: List[Dict]) -> pd.DataFrame:
        """
        Extract agent-level data from batch run results.
        
        Args:
            results: List of dictionaries from batch_run
            
        Returns:
            DataFrame with agent-level data or None if not available
        """
        agent_records = []
        
        for result in results:
            # Extract run metadata
            run_id = result.get('RunId', 0)
            iteration = result.get('iteration', 0)
            step = result.get('Step', 0)
            
            # Extract parameter values
            param_values = {}
            for param in self.variable_parameters.keys():
                if param in result:
                    param_values[param] = result[param]
            for param in self.fixed_parameters.keys():
                if param in result:
                    param_values[param] = result[param]
            
            # Check if agent data is available in the result
            # Mesa's batch_run stores agent data differently depending on datacollector setup
            if 'agent_vars' in result and result['agent_vars']:
                for agent_id, agent_data in result['agent_vars'].items():
                    agent_record = {
                        'RunId': run_id,
                        'Step': step,
                        'iteration': iteration,
                        'AgentID': agent_id,
                        **param_values,
                        **agent_data
                    }
                    agent_records.append(agent_record)
        
        if agent_records:
            return pd.DataFrame(agent_records)
        else:
            print("Warning: No agent data found in results. Agent reporters may not be configured in the model.")
            return None
    
    def save_results(self, model_data: pd.DataFrame, agent_data: pd.DataFrame, 
                    timestamp: str) -> None:
        """Save batch results to files."""
        model_file = self.output_dir / f"model_data_{timestamp}.csv"
        
        model_data.to_csv(model_file, index=False)
        
        print(f"Results saved:")
        print(f"  Model data: {model_file}")
        
        if agent_data is not None:
            agent_file = self.output_dir / f"agent_data_{timestamp}.csv"
            agent_data.to_csv(agent_file, index=False)
            print(f"  Agent data: {agent_file}")
        else:
            print("  Agent data: Not available")
        
        # Save metadata
        metadata = {
            "timestamp": timestamp,
            "variable_parameters": self.variable_parameters,
            "fixed_parameters": self.fixed_parameters,
            "iterations_per_combination": self.iterations_per_combination,
            "max_steps": self.max_steps,
            "total_runs": len(model_data['RunId'].unique()) if 'RunId' in model_data.columns else len(model_data),
            "parameter_combinations": self._count_combinations()
        }
        
        metadata_file = self.output_dir / f"metadata_{timestamp}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"  Metadata: {metadata_file}")
    
    def analyze_results(self, model_data: pd.DataFrame, agent_data: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of batch results.
        
        Args:
            model_data: Model-level data from batch runs
            agent_data: Agent-level data from batch runs (optional)
            
        Returns:
            Dictionary containing analysis results
        """
        print("\n" + "=" * 60)
        print("BATCH RESULTS ANALYSIS")
        print("=" * 60)
        
        analysis = {}
        
        # Check if we have the expected columns from the model's datacollector
        available_columns = model_data.columns.tolist()
        print(f"Available data columns: {available_columns}")
        
        # Try to identify final values for each run
        if 'RunId' in model_data.columns:
            final_model_data = model_data.groupby('RunId').last().reset_index()
        else:
            # If no RunId, treat each row as a separate run
            final_model_data = model_data.copy()
            final_model_data['RunId'] = range(len(final_model_data))
        
        # Basic statistics using available columns
        analysis['basic_stats'] = {
            'total_runs': len(final_model_data),
            'parameter_combinations': self._count_combinations(),
        }
        
        # Add metrics based on available columns
        metric_columns = ['Completed_Tasks', 'Average_Team_Efficacy', 'Average_PPS', 
                         'Average_Knowledge', 'Total_Tasks', 'Psychological_Safety']
        
        for metric in metric_columns:
            if metric in final_model_data.columns:
                analysis['basic_stats'][f'avg_final_{metric.lower()}'] = final_model_data[metric].mean()
        
        print(f"Total simulation runs: {analysis['basic_stats']['total_runs']}")
        print(f"Parameter combinations: {analysis['basic_stats']['parameter_combinations']}")
        
        for key, value in analysis['basic_stats'].items():
            if key.startswith('avg_final_'):
                print(f"Average final {key.replace('avg_final_', '').replace('_', ' ')}: {value:.3f}")
        
        # Parameter impact analysis
        print("\n--- Parameter Impact Analysis ---")
        
        # Analyze impact of each parameter on key outcomes
        for param in self.variable_parameters.keys():
            if param in final_model_data.columns:
                print(f"\n{param.upper()} IMPACT:")
                
                # Find available outcome metrics
                outcome_metrics = [col for col in ['Completed_Tasks', 'Average_Team_Efficacy', 'Average_PPS'] 
                                 if col in final_model_data.columns]
                
                if outcome_metrics:
                    param_analysis = final_model_data.groupby(param)[outcome_metrics].agg(['mean', 'std']).round(3)
                    print(param_analysis)
                    analysis[f'{param}_impact'] = param_analysis.to_dict()
                else:
                    print("  No suitable outcome metrics found for analysis")
        
        # Find optimal configurations
        print("\n--- Optimal Configurations ---")
        
        if 'Completed_Tasks' in final_model_data.columns:
            # Best for task completion
            best_tasks_idx = final_model_data['Completed_Tasks'].idxmax()
            best_tasks_config = final_model_data.loc[best_tasks_idx]
            print(f"Best for task completion ({best_tasks_config['Completed_Tasks']} tasks):")
            for param in self.variable_parameters.keys():
                if param in best_tasks_config:
                    print(f"  {param}: {best_tasks_config[param]}")
        
        if 'Average_Team_Efficacy' in final_model_data.columns:
            # Best for team efficacy  
            best_efficacy_idx = final_model_data['Average_Team_Efficacy'].idxmax()
            best_efficacy_config = final_model_data.loc[best_efficacy_idx]
            print(f"\nBest for team efficacy ({best_efficacy_config['Average_Team_Efficacy']:.3f}):")
            for param in self.variable_parameters.keys():
                if param in best_efficacy_config:
                    print(f"  {param}: {best_efficacy_config[param]}")
        
        # Store optimal configs if available
        analysis['optimal_configs'] = {}
        if 'Completed_Tasks' in final_model_data.columns:
            analysis['optimal_configs']['best_tasks'] = best_tasks_config.to_dict()
        if 'Average_Team_Efficacy' in final_model_data.columns:
            analysis['optimal_configs']['best_efficacy'] = best_efficacy_config.to_dict()
        
        # Correlation analysis
        print("\n--- Correlation Analysis ---")
        correlation_cols = list(self.variable_parameters.keys()) + \
                          ['Completed_Tasks', 'Average_Team_Efficacy', 'Average_PPS', 'Average_Knowledge']
        available_cols = [col for col in correlation_cols if col in final_model_data.columns]
        
        if len(available_cols) > 2:
            correlations = final_model_data[available_cols].corr()
            print("Key correlations with outcomes:")
            
            outcome_cols = ['Completed_Tasks', 'Average_Team_Efficacy', 'Average_PPS']
            for outcome in outcome_cols:
                if outcome in correlations.columns:
                    print(f"\n{outcome}:")
                    corr_series = correlations[outcome].sort_values(key=abs, ascending=False)[1:]  # Exclude self-correlation
                    for var, corr in corr_series.head(5).items():
                        print(f"  {var}: {corr:.3f}")
            
            analysis['correlations'] = correlations.to_dict()
        
        return analysis
    
    def generate_report(self, model_data: pd.DataFrame, agent_data: pd.DataFrame = None, 
                       analysis: Dict[str, Any] = None, save_to_file: bool = True) -> str:
        """
        Generate a comprehensive report of the batch run results.
        
        Args:
            model_data: Model-level data
            agent_data: Agent-level data (optional)
            analysis: Analysis results from analyze_results() (optional)
            save_to_file: Whether to save the report to a file
            
        Returns:
            Report as a string
        """
        if analysis is None:
            analysis = self.analyze_results(model_data, agent_data)
            
        timestamp = model_data['timestamp'].iloc[0] if 'timestamp' in model_data.columns else datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report = f"""
# TEAMS CORE BATCH SIMULATION REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Timestamp: {timestamp}

## SIMULATION CONFIGURATION
- Parameter combinations tested: {self._count_combinations()}
- Iterations per combination: {self.iterations_per_combination}
- Total simulation runs: {analysis['basic_stats']['total_runs']}
- Maximum steps per run: {self.max_steps}

## PARAMETER SPACE
"""
        
        for param, values in self.variable_parameters.items():
            report += f"- {param}: {values}\n"
        
        report += f"""
## OVERALL RESULTS
"""
        
        # Add available results
        for key, value in analysis['basic_stats'].items():
            if key.startswith('avg_final_'):
                metric_name = key.replace('avg_final_', '').replace('_', ' ').title()
                report += f"- Average final {metric_name}: {value:.3f}\n"
        
        report += f"""
## OPTIMAL CONFIGURATIONS
"""
        
        if 'optimal_configs' in analysis and 'best_tasks' in analysis['optimal_configs']:
            report += f"""
### Best for Task Completion
- Completed Tasks: {analysis['optimal_configs']['best_tasks'].get('Completed_Tasks', 'N/A')}
"""
            for param in self.variable_parameters.keys():
                if param in analysis['optimal_configs']['best_tasks']:
                    report += f"- {param}: {analysis['optimal_configs']['best_tasks'][param]}\n"
        
        if 'optimal_configs' in analysis and 'best_efficacy' in analysis['optimal_configs']:
            report += f"""
### Best for Team Efficacy
- Team Efficacy: {analysis['optimal_configs']['best_efficacy'].get('Average_Team_Efficacy', 'N/A')}
"""
            for param in self.variable_parameters.keys():
                if param in analysis['optimal_configs']['best_efficacy']:
                    report += f"- {param}: {analysis['optimal_configs']['best_efficacy'][param]}\n"
        
        report += "\n## RECOMMENDATIONS\n"
        
        # Generate recommendations based on analysis
        if 'RunId' in model_data.columns:
            final_model_data = model_data.groupby('RunId').last().reset_index()
        else:
            final_model_data = model_data.copy()
        
        # Find parameters that consistently lead to better outcomes
        recommendations = []
        
        outcome_column = None
        for col in ['Completed_Tasks', 'Average_Team_Efficacy', 'Average_PPS']:
            if col in final_model_data.columns:
                outcome_column = col
                break
        
        if outcome_column:
            for param in self.variable_parameters.keys():
                if param in final_model_data.columns:
                    param_groups = final_model_data.groupby(param)[outcome_column].mean()
                    if len(param_groups) > 1:
                        best_value = param_groups.idxmax()
                        worst_value = param_groups.idxmin()
                        improvement = param_groups[best_value] - param_groups[worst_value]
                        if improvement > 0.01:  # Some improvement threshold
                            recommendations.append(f"- Setting {param} to {best_value} improves {outcome_column} by {improvement:.3f} on average")
        
        if recommendations:
            report += "\n".join(recommendations)
        else:
            report += "- No strong parameter recommendations found. Results may vary significantly based on random factors."
        
        report += f"""

## DATA FILES GENERATED
- Model data: model_data_{timestamp}.csv
"""
        if agent_data is not None:
            report += f"- Agent data: agent_data_{timestamp}.csv\n"
        report += f"""- Metadata: metadata_{timestamp}.json
- Report: batch_report_{timestamp}.md

"""
        
        if save_to_file:
            report_file = self.output_dir / f"batch_report_{timestamp}.md"
            with open(report_file, 'w') as f:
                f.write(report)
            print(f"Report saved to: {report_file}")
        
        return report
    
    def run_focused_experiment(self, focus_params: Dict[str, List], 
                             iterations: int = 20) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Run a focused experiment with a smaller parameter space for detailed analysis.
        
        Args:
            focus_params: Dictionary of parameters to vary
            iterations: Number of iterations per combination
            
        Returns:
            Tuple of (model_data, agent_data) DataFrames
        """
        print(f"\n=== FOCUSED EXPERIMENT ===")
        print(f"Parameters: {focus_params}")
        print(f"Iterations: {iterations}")
        
        # Temporarily replace variable parameters
        original_params = self.variable_parameters.copy()
        original_iterations = self.iterations_per_combination
        
        self.variable_parameters = focus_params
        self.iterations_per_combination = iterations
        
        try:
            model_data, agent_data = self.run_batch(save_intermediate=True)
            return model_data, agent_data
        finally:
            # Restore original parameters
            self.variable_parameters = original_params
            self.iterations_per_combination = original_iterations

