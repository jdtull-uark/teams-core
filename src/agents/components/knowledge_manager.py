from typing import Dict, List, Optional, Set, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from ..engineer import EngineerAgent
    from .knowledge_network import KnowledgeNetwork

class KnowledgeManager:
    """
    Handles all knowledge-related operations for an engineer agent.
    Focuses on the agent's own knowledge and delegates network operations.
    """
    
    def __init__(self, agent: 'EngineerAgent'):
        self.agent = agent
        self.learned_knowledge: Set[str] = set()
        self.concept_learning_progress: Dict[str, float] = {}  # {concept_id: progress (0-1)}
        
        self._knowledge_network: Optional['KnowledgeNetwork'] = None

    def set_knowledge_network(self, knowledge_network: 'KnowledgeNetwork') -> None:
        """Set the knowledge network dependency."""
        self._knowledge_network = knowledge_network

    @property
    def knowledge_network(self) -> 'KnowledgeNetwork':
        """Get the knowledge network, using agent's network if not set."""
        if self._knowledge_network is None:
            return self.agent.knowledge_network
        return self._knowledge_network

    def has_knowledge(self, concept: str) -> bool:
        """Check if the agent knows a specific concept."""
        return concept in self.learned_knowledge

    def get_missing_knowledge(self, required_concepts: Optional[List[str]] = None) -> List[str]:
        """
        Get a list of knowledge concepts needed for the current subtask or provided list.
        """
        if required_concepts is None:
            if not self.agent.tasking.current_subtask:
                return []
            required_concepts = self.agent.tasking.current_subtask.required_knowledge


        return [concept for concept in required_concepts if concept not in self.learned_knowledge]

    def has_all_required_knowledge(self, required_concepts: Optional[List[str]] = None) -> bool:
        """Check if agent has all knowledge required for current subtask or provided list."""
        if required_concepts is None:
            if not self.agent.tasking.current_subtask:
                return True
            required_concepts = self.agent.tasking.current_subtask.required_knowledge
        
        return all(concept in self.learned_knowledge for concept in required_concepts)

    def learn_concept(self, concept: str) -> bool:
        """
        Attempt to learn a concept. Returns True if concept was learned this step.
        """
        if concept in self.learned_knowledge:
            return False

        if concept not in self.concept_learning_progress:
            self.concept_learning_progress[concept] = 0.0

        progress_increment = (
            self.agent.learning_rate * 
            self.agent.work_efficiency * 
            random.uniform(0.5, 1.5)
        )

        self.concept_learning_progress[concept] += progress_increment

        if self.concept_learning_progress[concept] >= 1.0:
            # Concept learned
            self.learned_knowledge.add(concept)
            self.agent._log_history("knowledge_learned", {"concept": concept})
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
            self.knowledge_network.add_agent_knowledge(sender_id, concept)
            # Log the knowledge share
            self.agent._log_history("knowledge_share_received", {
                "sender_id": sender_id,
                "shared_concept": concept
            })
            return True
        else:
            # Still update network knowledge even if we already knew it
            self.knowledge_network.add_agent_knowledge(sender_id, concept)
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
            if not self.agent.tasking.current_subtask:
                return []
            required_concepts = self.agent.tasking.current_subtask.required_knowledge

        missing_concepts = self.get_missing_knowledge(required_concepts)
        if not missing_concepts:
            return []

        # Find agents with any of the missing knowledge
        agents_with_knowledge = self.knowledge_network.find_agents_with_any_knowledge(missing_concepts)
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
            "learned_concepts": len(self.learned_knowledge),
            "concepts_in_progress": len(self.concept_learning_progress),
            "network_agents": self.knowledge_network.get_network_size(),
            "network_knowledge_entries": self.knowledge_network.get_total_knowledge_entries(),
            "learned_knowledge": list(self.learned_knowledge),
            "learning_progress": self.concept_learning_progress.copy()
        }

    def knows_agent_with_knowledge(self, concept: str) -> bool:
        """Check if we know any agent has a specific knowledge concept."""
        return self.knowledge_network.knows_any_agent_with_knowledge(concept)

    def get_agents_with_knowledge(self, concept: str) -> List[str]:
        """Get list of agent IDs that we know have a specific knowledge concept."""
        return self.knowledge_network.get_agents_with_knowledge(concept)

    def update_agent_knowledge(self, unique_id: str, concept: str) -> None:
        """Update our knowledge of what another agent knows."""
        self.knowledge_network.add_agent_knowledge(unique_id, concept)