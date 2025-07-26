from typing import List, Dict, Set, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..engineer import EngineerAgent

class KnowledgeNetwork:
    """
    Manages knowledge about other agents' capabilities.
    Focused solely on tracking what other agents know.
    """
    
    def __init__(self):
        # Use str for agent IDs to be consistent with Task system
        self.network: Dict[str, Set[str]] = {}

    def knows_agent_has_knowledge(self, unique_id: str, concept: str) -> bool:
        """Check if we know an agent has specific knowledge."""
        return unique_id in self.network and concept in self.network[unique_id]

    def knows_any_agent_with_knowledge(self, concept: str) -> bool:
        """Check if we know any agent has a specific knowledge concept."""
        return any(concept in concepts for concepts in self.network.values())

    def get_agents_with_knowledge(self, concept: str) -> List[str]:
        """Get all agents known to have specific knowledge."""
        return [
            unique_id for unique_id, concepts in self.network.items()
            if concept in concepts
        ]

    def add_agent_knowledge(self, unique_id: str, concept: str) -> None:
        """Record that an agent has specific knowledge."""
        if unique_id not in self.network:
            self.network[unique_id] = set()
        self.network[unique_id].add(concept)

    def add_agent_knowledge_bulk(self, unique_id: str, concepts: List[str]) -> None:
        """Record multiple knowledge concepts for an agent."""
        if unique_id not in self.network:
            self.network[unique_id] = set()
        self.network[unique_id].update(concepts)

    def get_agent_knowledge(self, unique_id: str) -> Set[str]:
        """Get all knowledge concepts we know an agent has."""
        return self.network.get(unique_id, set()).copy()

    def remove_agent(self, unique_id: str) -> None:
        """Remove an agent from the network."""
        self.network.pop(unique_id, None)

    def get_network_size(self) -> int:
        """Get the number of agents in the network."""
        return len(self.network)

    def get_total_knowledge_entries(self) -> int:
        """Get the total number of knowledge entries across all agents."""
        return sum(len(concepts) for concepts in self.network.values())

    def find_agents_with_any_knowledge(self, concepts: List[str]) -> Dict[str, List[str]]:
        """
        Find agents who have any of the specified knowledge concepts.
        Returns dict mapping unique_id to list of concepts they have.
        """
        result = {}
        for unique_id, agent_concepts in self.network.items():
            matching_concepts = [concept for concept in concepts if concept in agent_concepts]
            if matching_concepts:
                result[unique_id] = matching_concepts
        return result

    def clear(self) -> None:
        """Clear all network data."""
        self.network.clear()

