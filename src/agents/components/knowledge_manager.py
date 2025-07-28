# src/agents/components/knowledge_manager.py
from typing import Dict, List, Optional, Set, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from ..engineer import EngineerAgent
    from .knowledge_network import KnowledgeNetwork

class KnowledgeManager:
    """
    Handles all knowledge-related operations for an engineer agent.
    Includes integrated knowledge registry for tracking other agents' knowledge.
    """
    
    def __init__(self):
        self.learned_knowledge: Set[str] = set()
        self.concept_learning_progress: Dict[str, float] = {}  # {concept_id: progress (0-1)}
        
        # Integrated knowledge registry
        from .knowledge_network import KnowledgeNetwork
        self._knowledge_network = KnowledgeNetwork()

    def has_knowledge(self, concept: str) -> bool:
        """Check if the agent knows a specific concept."""
        return concept in self.learned_knowledge

    def get_missing_knowledge(self, required_concepts: Optional[List[str]] = None) -> List[str]:
        """
        Get a list of knowledge concepts needed for the current subtask or provided list.
        """
        if required_concepts is None:
            if not hasattr(self, 'current_subtask') or not self.current_subtask:
                return []
            required_concepts = self.current_subtask.required_knowledge

        return [concept for concept in required_concepts if concept not in self.learned_knowledge]

    def has_all_required_knowledge(self, required_concepts: Optional[List[str]] = None) -> bool:
        """Check if agent has all knowledge required for current subtask or provided list."""
        if required_concepts is None:
            if not hasattr(self, 'current_subtask') or not self.current_subtask:
                return True
            required_concepts = self.current_subtask.required_knowledge
        
        return all(concept in self.learned_knowledge for concept in required_concepts)

    def learn_concept(self, concept: str) -> bool:
        """
        Attempt to learn a concept. Returns True if concept was learned this step.
        """
        if concept in self.learned_knowledge:
            return False

        if concept not in self.concept_learning_progress:
            self.concept_learning_progress[concept] = 0.0

        # Access learning_rate and work_efficiency from the main agent
        learning_rate = getattr(self, 'learning_rate', 0.05)
        work_efficiency = getattr(self, 'work_efficiency', 1.0)
        
        progress_increment = (
            learning_rate * 
            work_efficiency * 
            random.uniform(0.5, 1.5)
        )

        self.concept_learning_progress[concept] += progress_increment

        if self.concept_learning_progress[concept] >= 1.0:
            # Concept learned
            self.learned_knowledge.add(concept)
            if hasattr(self, '_log_history'):
                self._log_history("knowledge_learned", {"concept": concept})
            del self.concept_learning_progress[concept]
            return True

        return False

    def receive_shared_knowledge(self, sender_id: str, concept: str) -> bool:
        """
        Receive knowledge shared from another agent.
        Returns True if this was new knowledge.
        """
        if concept not in self.learned_knowledge:
            self.learned_knowledge.add(concept)
            # Update knowledge network about the sender
            self._knowledge_network.add_agent(sender_id, concept)
            # Log the knowledge share
            if hasattr(self, '_log_history'):
                self._log_history("knowledge_share_received", {
                    "sender_id": sender_id,
                    "shared_concept": concept
                })
            return True
        else:
            # Still update network knowledge even if we already knew it
            self._knowledge_network.add_agent(sender_id, concept)
            return False

    def get_shareable_knowledge(self, requested_concepts: List[str]) -> List[str]:
        """Get concepts that we can share from the requested list."""
        return [concept for concept in requested_concepts 
                if concept in self.learned_knowledge]

    def find_agents_with_needed_knowledge(self, required_concepts: Optional[List[str]] = None) -> List[str]:
        """
        Find agents who have knowledge needed for current subtask or provided concepts.
        Returns list of agent IDs.
        """
        if required_concepts is None:
            if not hasattr(self, 'current_subtask') or not self.current_subtask:
                return []
            required_concepts = self.current_subtask.required_knowledge

        missing_concepts = self.get_missing_knowledge(required_concepts)
        if not missing_concepts:
            return []

        # Find agents with any of the missing knowledge
        agents_with_knowledge = self._knowledge_network.find_agents_with_any_knowledge(missing_concepts)
        return list(agents_with_knowledge.keys())

    def get_learning_progress(self, concept: str) -> float:
        """Get the learning progress for a specific concept (0.0 to 1.0)."""
        if concept in self.learned_knowledge:
            return 1.0
        return self.concept_learning_progress.get(concept, 0.0)

    def get_all_learning_progress(self) -> Dict[str, float]:
        """Get learning progress for all concepts currently being learned."""
        return self.concept_learning_progress.copy()

    def reset_learning_progress(self, concept: str) -> None:
        """Reset learning progress for a specific concept."""
        self.concept_learning_progress.pop(concept, None)

    def get_knowledge_stats(self) -> Dict[str, any]:
        """Get statistics about the agent's knowledge."""
        return {
            "learned_knowledge": list(self.learned_knowledge),
            "concepts_in_progress": len(self.concept_learning_progress),
            "learning_progress": self.concept_learning_progress.copy()
        }

    # Registry delegation methods
    def add_agent_knowledge(self, unique_id: str, concept: str) -> None:
        """Record that an agent has specific knowledge."""
        self._knowledge_network.add_agent(unique_id, concept)

    def remove_agent_from_network(self, unique_id: str) -> None:
        """Remove an agent from the knowledge network."""
        self._knowledge_network.remove_agent(unique_id)

    def knows_agent_has_knowledge(self, unique_id: str, concept: str) -> bool:
        """Check if we know an agent has specific knowledge."""
        return self._knowledge_network.knows_agent_has_knowledge(unique_id, concept)

    def knows_any_agent_with_knowledge(self, concept: str) -> bool:
        """Check if we know any agent has a specific knowledge concept."""
        return self._knowledge_network.knows_any_agent_with_knowledge(concept)

    def get_agents_with_knowledge(self, concept: str) -> List[str]:
        """Get all agents known to have specific knowledge."""
        return self._knowledge_network.get_agents_with_knowledge(concept)

    def add_agent_knowledge_bulk(self, unique_id: str, concepts: List[str]) -> None:
        """Record multiple knowledge concepts for an agent."""
        self._knowledge_network.add_agent_knowledge_bulk(unique_id, concepts)

    def get_agent_knowledge(self, unique_id: str) -> Set[str]:
        """Get all knowledge concepts we know an agent has."""
        return self._knowledge_network.get_agent_knowledge(unique_id)

    def find_agents_with_any_knowledge(self, concepts: List[str]) -> Dict[str, List[str]]:
        """
        Find agents who have any of the specified knowledge concepts.
        Returns dict mapping unique_id to list of concepts they have.
        """
        return self._knowledge_network.find_agents_with_any_knowledge(concepts)

    def get_network_size(self) -> int:
        """Get the number of agents in the knowledge network."""
        return self._knowledge_network.get_network_size()

    def get_total_knowledge_entries(self) -> int:
        """Get the total number of knowledge entries across all agents."""
        return self._knowledge_network.get_total_knowledge_entries()

    def clear_network(self) -> None:
        """Clear all network data."""
        self._knowledge_network.clear()