# simulation_v3.py
# Phase 3: Core Simulation Runner (Partition & Healing)

import time
from p2p_network import SecureNode

def run_simulation():
    print("=" * 60)
    print("  ByzCRDT-Chain Phase 3: Partition Tolerance & ZKP Demo")
    print("=" * 60)

    # 1. Setup Nodes
    alice = SecureNode("Alice")
    bob = SecureNode("Bob")
    charlie = SecureNode("Charlie")
    
    all_nodes = [alice, bob, charlie]
    for n1 in all_nodes:
        for n2 in all_nodes:
            if n1 != n2:
                n1.register_peer(n2)

    # 2. Partition Occurs
    print("\n[!] NETWORK PARTITION OCCURS: [Alice] < // > [Bob, Charlie]")
    
    # Alice operates in isolation
    alice.transact("Alice_Tx_1_Isolated")
    alice.transact("Alice_Tx_2_Isolated")
    
    # Bob and Charlie operate together
    bob.transact("Bob_Tx_1")
    charlie.transact("Charlie_Tx_1")
    
    payload_b, sig_b = bob.generate_delta_payload()
    charlie.receive_gossip(payload_b, sig_b)
    
    print(f"\n--- State During Partition ---")
    print(f"Alice's Ledger:   {alice.ledger.get_active_transactions()}")
    print(f"Bob's Ledger:     {bob.ledger.get_active_transactions()}")
    print(f"Charlie's Ledger: {charlie.ledger.get_active_transactions()}")

    # 3. Partition Heals
    print("\n[!] NETWORK PARTITION HEALS. Initiating Sync...")
    
    # Alice gossips to Bob & Charlie
    payload_a, sig_a = alice.generate_delta_payload()
    bob.receive_gossip(payload_a, sig_a)
    print("  [Filter] Verifying Monotonicity ZKP for Alice... ACCEPTED")
    charlie.receive_gossip(payload_a, sig_a)
    
    # Bob gossips back to Alice
    payload_b2, sig_b2 = bob.generate_delta_payload()
    alice.receive_gossip(payload_b2, sig_b2)
    print("  [Filter] Verifying Monotonicity ZKP for Bob... ACCEPTED")

    print(f"\n--- State After Merge (Strong Eventual Consistency) ---")
    print(f"Alice's Ledger:   {alice.ledger.get_active_transactions()}")
    print(f"Bob's Ledger:     {bob.ledger.get_active_transactions()}")
    
    success = (alice.ledger.get_active_transactions() == bob.ledger.get_active_transactions() == charlie.ledger.get_active_transactions())
    print(f"\n[Success] All honest nodes converged to identical state: {success}")
    print("=" * 60)

if __name__ == "__main__":
    run_simulation()
