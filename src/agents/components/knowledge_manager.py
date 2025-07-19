from typing import Dict, List, Optional, Set, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from ..engineer import EngineerAgent

class KnowledgeManager:
    """Handles all knowledge-related operations for an engineer agent."""
    
    def __init__(self, agent: 'EngineerAgent'):
        self.agent = agent
        self.learned_knowledge: Set[str] = set()
        self.knowledge_network: Dict[int, Set[str]] = {}  # {agent_id: {concepts}}
        self.concept_learning_progress: Dict[str, float] = {}  # {concept_id: progress (0-1)}
    
    def get_missing_knowledge(self) -> List[str]:
        """Get a list of knowledge concepts needed for the current subtask."""
        if not self.agent.current_subtask:
            return []
        
        missing_knowledge = []
        needed_knowledge = self.agent.current_subtask.required_knowledge

        for concept in needed_knowledge:
            if concept not in self.learned_knowledge:
                missing_knowledge.append(concept)

        return missing_knowledge
    
    def has_all_required_knowledge(self) -> bool:
        """Check if agent has all knowledge required for current subtask."""
        if not self.agent.current_subtask:
            return True
        
        return all(
            concept in self.learned_knowledge 
            for concept in self.agent.current_subtask.required_knowledge
        )
    
    def learn_concept(self, concept: str) -> bool:
        """Attempt to learn a concept. Returns True if concept was learned."""
        if concept not in self.concept_learning_progress:
            self.concept_learning_progress[concept] = 0.0
        
        # Progress learning based on agent's learning rate and work efficiency
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
    
    def receive_shared_knowledge(self, sender_id: int, concept: str):
        """Receive knowledge shared from another agent."""
        if concept not in self.learned_knowledge:
            self.learned_knowledge.add(concept)
            # Update knowledge network
            self.knowledge_network.setdefault(sender_id, set()).add(concept)
            # Log the knowledge share
            self.agent._log_history("knowledge_share_received", {
                "sender_id": sender_id,
                "shared_concept": concept
            })
    
    def knows_agent_has_knowledge(self, agent_id: int, concept: str) -> bool:
        """Check if we know that a specific agent has a specific knowledge concept."""
        return (agent_id in self.knowledge_network and 
                concept in self.knowledge_network[agent_id])

    def knows_agent_with_knowledge(self, concept: str) -> bool:
        """Check if we know any agent has a specific knowledge concept."""
        return any(concept in concepts for concepts in self.knowledge_network.values())
    
    def get_agents_with_knowledge(self, concept: str) -> List[int]:
        """Get list of agent IDs that we know have a specific knowledge concept."""
        return [agent_id for agent_id, concepts in self.knowledge_network.items() 
                if concept in concepts]
    
    def find_agents_with_needed_knowledge(self) -> List[int]:
        """Find agents who have knowledge needed for current subtask."""
        if not self.agent.current_subtask:
            return []
        
        potential_targets = []
        needed_knowledge = self.agent.current_subtask.required_knowledge
        
        for concept in needed_knowledge:
            # Only look for knowledge we don't already have
            if concept not in self.learned_knowledge:
                # Find agents we know have this knowledge
                agents_with_knowledge = self.get_agents_with_knowledge(concept)
                potential_targets.extend(agents_with_knowledge)
        
        # Remove duplicates and return
        return list(set(potential_targets))
    
    def update_knowledge_network(self, agent_id: int, concept: str):
        """Update our knowledge of what other agents know."""
        self.knowledge_network.setdefault(agent_id, set()).add(concept)
    
    def get_shareable_knowledge(self, requested_concepts: List[str]) -> List[str]:
        """Get concepts that we can share from the requested list."""
        return [concept for concept in requested_concepts 
                if concept in self.learned_knowledge]