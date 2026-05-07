# p2p_network.py
# Phase 3: P2P Network Protocol with Partition Tolerance

import time
from crypto_zkp import CryptoManager, MonotonicZKP
from ledger_orset import ByzLedger

class SecureNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.private_key, self.public_key = CryptoManager.generate_keys()
        self.peer_keys = {} # node_id -> public_key
        self.ledger = ByzLedger(node_id)
        
        # State tracking for Monotonicity Proofs (simulating a sequence counter)
        self.state_counter = 0 
        self.blacklist = set()

    def register_peer(self, peer_node):
        self.peer_keys[peer_node.node_id] = peer_node.public_key

    def transact(self, data):
        self.ledger.record_transaction(data)
        self.state_counter += 1
        print(f"  [{self.node_id}] Recorded Tx: '{data}' | State: {self.state_counter}")

    def generate_delta_payload(self):
        delta_state = self.ledger.transactions.get_state()
        
        # Phase 3 ZKP Simulation: Proving our state increased monotonically
        proof = MonotonicZKP.generate_proof(0, self.state_counter, "shared_zk_sim_key")
        
        payload = {
            "sender": self.node_id,
            "new_state_val": self.state_counter,
            "delta_added": delta_state["added"],
            "delta_removed": delta_state["removed"],
            "zk_proof": proof,
            "ts": time.time()
        }
        
        signature = CryptoManager.sign_data(self.private_key, payload)
        return payload, signature

    def receive_gossip(self, payload, signature):
        sender = payload["sender"]
        
        if sender in self.blacklist:
            return False

        if sender not in self.peer_keys:
            return False
            
        # 1. ECDSA Authentication
        if not CryptoManager.verify_signature(self.peer_keys[sender], payload, signature):
            print(f"  [Filter] Invalid ECDSA Signature from {sender}. Blacklisting.")
            self.blacklist.add(sender)
            return False
            
        # 2. ZKP Monotonicity Verification
        # In a real setup, old_val is tracked per peer. Using 0 for stateless sim demonstration.
        is_valid_proof = MonotonicZKP.verify_proof(0, payload["new_state_val"], payload["zk_proof"], "shared_zk_sim_key")
        if not is_valid_proof:
            print(f"  [Filter] Invalid ZK-Monotonicity Proof from {sender}. Blacklisting.")
            self.blacklist.add(sender)
            return False
            
        # 3. CRDT Join-Semilattice Merge
        # Convert lists back to sets for merge
        remote_added = {k: set(v) for k, v in payload["delta_added"].items()}
        remote_removed = {k: set(v) for k, v in payload["delta_removed"].items()}
        
        self.ledger.transactions.merge(remote_added, remote_removed)
        return True
