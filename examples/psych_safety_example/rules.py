"""Psychological safety and productivity rules."""

import random
from typing import TYPE_CHECKING
from src.framework.core.interfaces import Rule

if TYPE_CHECKING:
    from src.framework.core.model import BaseModel

class PsychologicalSafetyRule(Rule):
    """Rule that manages psychological safety in the team."""
    
    def __init__(self, base_change_rate: float = 0.1):
        self.base_change_rate = base_change_rate

    def should_apply(self, model: 'BaseModel') -> bool:
        return True

    def apply(self, model: 'BaseModel') -> None:
        # For each agent, adjust pps based on interactions with other agents (via their cps)
        for agent in model.agents:
            if not hasattr(agent, 'perceived_psychological_safety'):
                continue
            # Default: no change if no interactions
            pps = agent.perceived_psychological_safety
            # Try to get recent interactions from agent's communication_manager, if available
            comm = getattr(agent, 'get_component', None)
            interaction_partners = []
            if comm:
                cm = agent.get_component('communication_manager')
                if cm and hasattr(cm, 'interaction_history') and cm.interaction_history:
                    # Only consider interactions from the last step
                    last_step = model.step_count - 1
                    recent = [entry for entry in cm.interaction_history if entry.get('step') == last_step]
                    for entry in recent:
                        rid = entry.get('recipient')
                        if rid is not None and rid != agent.unique_id:
                            partner = model.get_agent_by_id(rid)
                            if partner:
                                interaction_partners.append(partner)
            # If no recent partners, skip
            if not interaction_partners:
                continue
            # For each partner, move pps a small step toward their cps
            for partner in interaction_partners:
                cps = getattr(partner, 'contributed_psychological_safety', 0.0)
                
                delta = cps * self.base_change_rate * model.random.uniform(0.5, 1.5)
                agent.perceived_psychological_safety += delta
                agent.perceived_psychological_safety = max(0.0, min(1.0, agent.perceived_psychological_safety))

            nonnorm_pps = agent.perceived_psychological_safety * 2 - 1
            cps_delta = nonnorm_pps * self.base_change_rate * model.random.uniform(0.5, 1.5)
            agent.contributed_psychological_safety += delta
            agent.contributed_psychological_safety = max(-1.0, min(1.0, agent.contributed_psychological_safety))


    def preprocess_interaction(self, initiator, recipient, interaction_type: str, context: any):
        # For knowledge/collaboration interactions, use initiator's cps and recipient's pps to determine willingness.
        if interaction_type in ["knowledge_share", "knowledge_request", "collaboration"]:
            cps = getattr(initiator, 'contributed_psychological_safety', 0.0)
            pps = getattr(recipient, 'perceived_psychological_safety', 0.5)
            # Normalize cps to [0,1]
            norm_cps = (cps + 1) / 2
            # Willingness is a weighted average of normalized cps and pps
            willingness = 0.2 * norm_cps + 0.8 * pps
            # Add a small random factor
            willingness = min(1.0, max(0.0, willingness + random.uniform(-0.1, 0.1)))
            
            context['knowledge_share_modifier'] = willingness

            return True, context
        return False, context

class ProductivityRule(Rule):
    """Rule that affects productivity based on various factors."""
    
    def should_apply(self, model: 'BaseModel') -> bool:
        """Apply every 10 steps."""
        return model.step_count % 10 == 0
    
    def apply(self, model: 'BaseModel') -> None:
        """Adjust agent productivity based on psychological safety and other factors."""
        for agent in model.agents:
            if hasattr(agent, 'work_efficiency') and hasattr(agent, 'perceived_psychological_safety'):
                # Higher psychological safety improves efficiency
                if agent.perceived_psychological_safety > 0.7:
                    agent.work_efficiency = min(2.0, agent.work_efficiency + 0.05)
                elif agent.perceived_psychological_safety < 0.3:
                    agent.work_efficiency = max(0.1, agent.work_efficiency - 0.05)
