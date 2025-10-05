"""
Vector Clock Implementation for Distributed Systems

A vector clock is a data structure used for determining the partial ordering of events
in a distributed system and detecting causality violations.
"""

from typing import Dict, Tuple, Any
import json


class VectorClock:
    """
    Vector clock implementation for tracking causality in distributed systems.
    
    Each node maintains a vector of counters, one for each node in the system.
    The vector clock captures the causal relationships between events.
    """
    
    def __init__(self, node_id: str, all_nodes: list = None):
        """
        Initialize vector clock for a node.
        
        Args:
            node_id: Identifier for this node
            all_nodes: List of all node IDs in the system (optional)
        """
        self.node_id = node_id
        self.clock = {}
        
        # Initialize with all known nodes
        if all_nodes:
            for node in all_nodes:
                self.clock[node] = 0
        else:
            self.clock[node_id] = 0
    
    def increment(self, node_id: str = None) -> 'VectorClock':
        """
        Increment the counter for the specified node (or self if not specified).
        
        Args:
            node_id: Node to increment (defaults to self)
            
        Returns:
            Self for chaining
        """
        if node_id is None:
            node_id = self.node_id
            
        if node_id not in self.clock:
            self.clock[node_id] = 0
        self.clock[node_id] += 1
        return self
    
    def update(self, other_clock: 'VectorClock') -> 'VectorClock':
        """
        Update this vector clock by merging with another vector clock.
        For each node, take the maximum of the two values.
        
        Args:
            other_clock: Another vector clock to merge with
            
        Returns:
            Self for chaining
        """
        # Add any new nodes from other clock
        for node, value in other_clock.clock.items():
            if node not in self.clock:
                self.clock[node] = 0
            self.clock[node] = max(self.clock[node], value)
        return self
    
    def compare(self, other_clock: 'VectorClock') -> str:
        """
        Compare this vector clock with another to determine the relationship.
        
        Returns:
            'happens-before' (→): this clock happened before other
            'happens-after' (←): this clock happened after other  
            'concurrent' (‖): clocks are concurrent
            'equal' (=): clocks are equal
        """
        if not isinstance(other_clock, VectorClock):
            raise TypeError("Can only compare with another VectorClock")
        
        # Get all unique nodes from both clocks
        all_nodes = set(self.clock.keys()) | set(other_clock.clock.keys())
        
        # Initialize comparison flags
        self_greater = False
        other_greater = False
        
        for node in all_nodes:
            self_val = self.clock.get(node, 0)
            other_val = other_clock.clock.get(node, 0)
            
            if self_val > other_val:
                self_greater = True
            elif other_val > self_val:
                other_greater = True
        
        # Determine relationship
        if self_greater and not other_greater:
            return 'happens-after'
        elif other_greater and not self_greater:
            return 'happens-before'
        elif not self_greater and not other_greater:
            return 'equal'
        else:
            return 'concurrent'
    
    def to_dict(self) -> Dict[str, int]:
        """Convert vector clock to dictionary for JSON serialization."""
        return dict(self.clock)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], node_id: str) -> 'VectorClock':
        """Create vector clock from dictionary."""
        vc = cls(node_id)
        vc.clock = {k: int(v) for k, v in data.items()}
        return vc
    
    def __str__(self) -> str:
        """String representation of the vector clock."""
        return f"VC({self.node_id}): {self.clock}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"VectorClock(node_id='{self.node_id}', clock={self.clock})"
    
    def __eq__(self, other) -> bool:
        """Check if two vector clocks are equal."""
        if not isinstance(other, VectorClock):
            return False
        return self.clock == other.clock


def test_vector_clock():
    """Test vector clock operations with a simple scenario."""
    print("=== Vector Clock Test ===")
    
    # Create clocks for nodes A and B
    clock_a = VectorClock("A", ["A", "B"])
    clock_b = VectorClock("B", ["A", "B"])
    
    print(f"Initial: A={clock_a}, B={clock_b}")
    print(f"Relationship: {clock_a.compare(clock_b)}")
    
    # A increments first
    clock_a.increment()
    print(f"\nAfter A increments: A={clock_a}, B={clock_b}")
    print(f"Relationship: {clock_a.compare(clock_b)}")
    
    # B increments
    clock_b.increment()
    print(f"\nAfter B increments: A={clock_a}, B={clock_b}")
    print(f"Relationship: {clock_a.compare(clock_b)}")
    
    # A increments again
    clock_a.increment()
    print(f"\nAfter A increments again: A={clock_a}, B={clock_b}")
    print(f"Relationship: {clock_a.compare(clock_b)}")
    
    # B updates with A's clock
    clock_b.update(clock_a)
    print(f"\nAfter B updates with A: A={clock_a}, B={clock_b}")
    print(f"Relationship: {clock_a.compare(clock_b)}")
    
    # Test concurrent scenario
    clock_c = VectorClock("C", ["A", "B", "C"])
    clock_c.increment()
    print(f"\nNew node C: A={clock_a}, C={clock_c}")
    print(f"Relationship: {clock_a.compare(clock_c)}")


if __name__ == "__main__":
    test_vector_clock()
