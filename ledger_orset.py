# ledger_orset.py
# Phase 3: OR-Set (Observed-Remove Set) Ledger for Transaction Management

import time
import hashlib

class ORSet:
    def __init__(self, node_id):
        self.node_id = node_id
        self.added = {}    # element -> set(tags)
        self.removed = {}  # element -> set(tags)

    def add(self, element):
        tag = f"{self.node_id}-{time.time_ns()}"
        if element not in self.added:
            self.added[element] = set()
        self.added[element].add(tag)
        return tag

    def remove(self, element):
        if element not in self.added:
            return False
        if element not in self.removed:
            self.removed[element] = set()
        # Tombstone all observed tags for this element
        for tag in self.added[element]:
            self.removed[element].add(tag)
        return True

    def elements(self):
        # Result = Added - Removed
        result = set()
        for elem, tags in self.added.items():
            active_tags = tags - self.removed.get(elem, set())
            if active_tags:
                result.add(elem)
        return result

    def merge(self, other_added, other_removed):
        # Join-Semilattice Merge Rule: Union of added, Union of removed
        for elem, tags in other_added.items():
            if elem not in self.added:
                self.added[elem] = set()
            self.added[elem].update(tags)
            
        for elem, tags in other_removed.items():
            if elem not in self.removed:
                self.removed[elem] = set()
            self.removed[elem].update(tags)

    def get_state(self):
        return {
            "added": {k: list(v) for k, v in self.added.items()},
            "removed": {k: list(v) for k, v in self.removed.items()}
        }

class ByzLedger:
    """The Ledger wrapping the OR-Set state."""
    def __init__(self, node_id):
        self.node_id = node_id
        self.transactions = ORSet(node_id)

    def record_transaction(self, tx_data):
        tx_id = hashlib.sha256(tx_data.encode()).hexdigest()[:12]
        self.transactions.add(tx_data)
        return tx_id
        
    def get_active_transactions(self):
        return self.transactions.elements()
