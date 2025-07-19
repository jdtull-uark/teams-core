from ..engineer import EngineerAgent
from typing import List, Optional, Dict, Any
import math

class MovementController:
    """Handles movement logic for agents in the simulation."""

    def get_closest_agent(self, targets: List['EngineerAgent']) -> Optional['EngineerAgent']:
        """Get the closest agent who has a specific knowledge concept."""
        if not targets:
            return None
        
        nearest_agent = None
        min_distance = float('inf')
        
        for agent_id in targets:
            target_agent = self.model.get_agent_by_id(agent_id)
            if target_agent and target_agent.pos:
                # Calculate Manhattan or Euclidean distance
                dx = abs(self.pos[0] - target_agent.pos[0])
                dy = abs(self.pos[1] - target_agent.pos[1])
                distance = dx + dy  # Manhattan distance
                # Or use: distance = math.sqrt(dx**2 + dy**2)  # Euclidean distance
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_agent = target_agent
        
        return nearest_agent

    
    def move_toward_agent(self, target: Optional['EngineerAgent']) -> bool:
        """Move toward the nearest agent in seeking_agent_targets."""
        if target:
            # Get possible moves
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
            
            # Find the move that gets us closest to the target
            best_move = None
            best_distance = float('inf')
            
            for step in possible_steps:
                dx = abs(self.pos[0] - target.pos[0])
                dy = abs(self.pos[1] - target.pos[1])
                distance = math.sqrt(dx**2 + dy**2)
                if distance < best_distance:
                    best_distance = distance
                    best_move = step
            
            if best_move:
                self.model.grid.move_agent(self, best_move)
                return True
        
        return False