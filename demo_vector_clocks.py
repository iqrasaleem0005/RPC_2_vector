#!/usr/bin/env python3
"""
Vector Clock Demonstration for Distributed Systems

This script demonstrates vector clock operations and causality relationships
in a simulated distributed RPC system.
"""

from vector_clock import VectorClock
import json
import time


def simulate_rpc_with_vector_clocks():
    """Simulate RPC calls with vector clocks to demonstrate causality."""
    print("=== Vector Clock RPC Simulation ===")
    
    # Create vector clocks for different nodes
    server_clock = VectorClock("server", ["server", "clientA", "clientB"])
    client_a_clock = VectorClock("clientA", ["server", "clientA", "clientB"])
    client_b_clock = VectorClock("clientB", ["server", "clientA", "clientB"])
    
    print(f"Initial clocks:")
    print(f"  Server: {server_clock}")
    print(f"  Client A: {client_a_clock}")
    print(f"  Client B: {client_b_clock}")
    
    # Simulate RPC calls
    print("\n--- Client A calls /add(2,3) ---")
    # Client A increments before sending
    client_a_clock.increment()
    print(f"Client A clock before request: {client_a_clock}")
    
    # Server receives request and updates its clock
    server_clock.update(client_a_clock)
    server_clock.increment()
    print(f"Server clock after receiving A's request: {server_clock}")
    
    # Server sends response back to A
    client_a_clock.update(server_clock)
    print(f"Client A clock after response: {client_a_clock}")
    print(f"Result: add(2,3) = 5")
    
    print("\n--- Client B calls /multiply(4,5) (concurrent) ---")
    # Client B increments before sending
    client_b_clock.increment()
    print(f"Client B clock before request: {client_b_clock}")
    
    # Server receives request and updates its clock
    server_clock.update(client_b_clock)
    server_clock.increment()
    print(f"Server clock after receiving B's request: {server_clock}")
    
    # Server sends response back to B
    client_b_clock.update(server_clock)
    print(f"Client B clock after response: {client_b_clock}")
    print(f"Result: multiply(4,5) = 20")
    
    # Analyze causality
    print("\n--- Causality Analysis ---")
    print(f"Client A final clock: {client_a_clock}")
    print(f"Client B final clock: {client_b_clock}")
    print(f"Server final clock: {server_clock}")
    
    # Compare clocks
    ab_relationship = client_a_clock.compare(client_b_clock)
    as_relationship = client_a_clock.compare(server_clock)
    bs_relationship = client_b_clock.compare(server_clock)
    
    print(f"\nClock relationships:")
    print(f"  Client A vs Client B: {ab_relationship}")
    print(f"  Client A vs Server: {as_relationship}")
    print(f"  Client B vs Server: {bs_relationship}")
    
    # Demonstrate happens-before
    print("\n--- Demonstrating Happens-Before ---")
    print("Client A makes another request...")
    client_a_clock.increment()
    print(f"Client A clock: {client_a_clock}")
    
    server_clock.update(client_a_clock)
    server_clock.increment()
    print(f"Server clock: {server_clock}")
    
    client_a_clock.update(server_clock)
    print(f"Client A clock after update: {client_a_clock}")
    
    # Now compare with B's clock
    final_ab_relationship = client_a_clock.compare(client_b_clock)
    print(f"Final A vs B relationship: {final_ab_relationship}")


def demonstrate_concurrent_events():
    """Demonstrate concurrent events using vector clocks."""
    print("\n=== Concurrent Events Demonstration ===")
    
    # Create two independent clients
    client_x = VectorClock("clientX", ["clientX", "clientY"])
    client_y = VectorClock("clientY", ["clientX", "clientY"])
    
    print(f"Initial clocks:")
    print(f"  Client X: {client_x}")
    print(f"  Client Y: {client_y}")
    print(f"  Relationship: {client_x.compare(client_y)}")
    
    # Both clients make independent operations
    print("\nBoth clients make independent operations...")
    client_x.increment()
    client_y.increment()
    
    print(f"After independent operations:")
    print(f"  Client X: {client_x}")
    print(f"  Client Y: {client_y}")
    print(f"  Relationship: {client_x.compare(client_y)}")
    
    # Demonstrate information exchange
    print("\nClient X shares its clock with Client Y...")
    client_y.update(client_x)
    print(f"After information exchange:")
    print(f"  Client X: {client_x}")
    print(f"  Client Y: {client_y}")
    print(f"  Relationship: {client_x.compare(client_y)}")


def simulate_distributed_system():
    """Simulate a more complex distributed system scenario."""
    print("\n=== Complex Distributed System Simulation ===")
    
    # Create a system with 3 nodes
    nodes = ["node1", "node2", "node3"]
    clocks = {}
    
    # Initialize all clocks
    for node in nodes:
        clocks[node] = VectorClock(node, nodes)
    
    print("Initial state:")
    for node, clock in clocks.items():
        print(f"  {node}: {clock}")
    
    # Simulate a sequence of events
    events = [
        ("node1", "increment"),
        ("node2", "increment"),
        ("node1", "send_to", "node3"),
        ("node3", "increment"),
        ("node2", "send_to", "node3"),
        ("node3", "increment"),
    ]
    
    print("\nSimulating events:")
    for i, event in enumerate(events, 1):
        if len(event) == 2:
            node, action = event
            if action == "increment":
                clocks[node].increment()
                print(f"  {i}. {node} increments: {clocks[node]}")
        elif len(event) == 3:
            sender, action, receiver = event
            if action == "send_to":
                # Sender increments before sending
                clocks[sender].increment()
                # Receiver updates with sender's clock
                clocks[receiver].update(clocks[sender])
                print(f"  {i}. {sender} sends to {receiver}")
                print(f"     {sender}: {clocks[sender]}")
                print(f"     {receiver}: {clocks[receiver]}")
    
    # Final analysis
    print("\nFinal state:")
    for node, clock in clocks.items():
        print(f"  {node}: {clock}")
    
    # Compare all pairs
    print("\nPairwise relationships:")
    for i, node1 in enumerate(nodes):
        for j, node2 in enumerate(nodes):
            if i < j:  # Avoid duplicate comparisons
                relationship = clocks[node1].compare(clocks[node2])
                print(f"  {node1} vs {node2}: {relationship}")


if __name__ == "__main__":
    # Run all demonstrations
    simulate_rpc_with_vector_clocks()
    demonstrate_concurrent_events()
    simulate_distributed_system()
    
    print("\n=== Summary ===")
    print("Vector clocks successfully demonstrate:")
    print("✓ Happens-before relationships (→)")
    print("✓ Concurrent events (‖)")
    print("✓ Clock synchronization")
    print("✓ Causality detection in distributed systems")
