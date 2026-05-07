

# Conflict-Free DAG-Chain: A BFT Ledger via CRDTs (Phase 3)

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository contains the Phase 3 implementation of **ByzCRDT-Chain**, a novel distributed ledger architecture. This project solves a critical open problem in distributed systems: achieving Byzantine Fault Tolerance (BFT) in a high-throughput, eventually consistent system without relying on slow, global consensus mechanisms like Proof-of-Work or voting.

By leveraging the mathematical properties of **Conflict-Free Replicated Data Types (CRDTs)** and a custom **Cryptographic Delta Proof (CDP)** layer, the system allows for zero-latency local transactions and is mathematically guaranteed to converge to a consistent state, even in the presence of malicious nodes and network partitions.

---

## System Architecture

The system's core innovation is its **Byzantine Filter**, which operates at the network ingestion layer. Instead of voting on transaction order, each node independently verifies incoming "delta" payloads against two strict criteria: cryptographic authenticity and algebraic monotonicity.

```mermaid
graph TD
    A[Client Transaction] --> B[Local OR-Set Update O1]

    B --> C{Generate Proofs}

    C --> D[ECDSA Signature]
    C --> E[ZKP Monotonicity Proof]

    D --> F[Gossip Delta Payload]
    E --> F

    F --> G{Peer Receives Payload}

    G --> H{Byzantine Filter}

    H -- Invalid --> I[Blacklist Sender]
    H -- Valid --> J[CRDT Merge Join-Semilattice]

    J --> K[Converged Global State]
```
Key Features (Phase 3 Upgrades)

  - Asymmetric Cryptography (ECDSA): Upgraded from symmetric keys to a full
    Public Key Infrastructure (PKI) for robust, non-repudiable transaction
    signing.
  - Zero-Knowledge Monotonicity Proofs: A Sigma-Protocol simulation ensures
    nodes can only append to their state history, cryptographically preventing
    illegal rollbacks or history deletion, even with a compromised key.
  - Advanced OR-Set Ledger: The ledger now uses an Observed-Remove Set (OR-Set),
    allowing it to manage a set of unique transaction hashes with conflict-free
    "add" and "remove" (tombstoning) capabilities.
  - Proven Partition Tolerance: The core simulation demonstrates that the system
    remains operational during a "split-brain" network partition and correctly
    merges divergent histories upon healing.

Repository Structure

This codebase is self-contained and does not require any external databases or
services.
```
.
├── crypto_zkp.py         # Handles ECDSA key management and ZKP logic.
├── ledger_orset.py       # Implements the core OR-Set CRDT data structure.
├── p2p_network.py        # Defines the SecureNode class and P2P gossip logic.
├── simulation_v3.py      # Main entry point: Runs the network partition demo.
├── metrics_v3.py         # Runs the performance benchmarking suite.
└── README.md             # This file.
```
Setup and Usage

This project has been tested on Python 3.10+. The only external dependency is
the cryptography library for ECDSA operations.

1. Clone the Repository

git clone https://github.com/Syed-Muhammad-Ahmer/Conflict-free-DAG-Chain.git


2. Install Dependencies

pip install cryptography

3. Run the Core Simulation (Network Partition Demo)

This script simulates a network of three nodes, partitions them, allows them to
diverge, and then heals the network to prove they converge to an identical
state.

python simulation_v3.py

Output:
```
============================================================
  ByzCRDT-Chain Phase 3: Partition Tolerance & ZKP Demo
============================================================

[!] NETWORK PARTITION OCCURS: [Alice] < // > [Bob, Charlie]
... (nodes transact in isolation) ...

[!] NETWORK PARTITION HEALS. Initiating Sync...
  [Filter] Verifying Monotonicity ZKP for Alice... ACCEPTED
  [Filter] Verifying Monotonicity ZKP for Bob... ACCEPTED

--- State After Merge (Strong Eventual Consistency) ---
Alice's Ledger:   {'Tx_A', 'Tx_B', 'Tx_C'}
Bob's Ledger:     {'Tx_A', 'Tx_B', 'Tx_C'}

[Success] All honest nodes converged to identical state: True
============================================================
```
4. Run the Performance Benchmarks

This script measures the computational overhead of the cryptographic operations
and compares the Phase 3 implementation against the Phase 2 baseline.

python metrics_v3.py

Expected Output:
```
=========================================================
  Phase 3 Performance Benchmarks (1000 Iterations)
=========================================================
  Phase 2 (HMAC) Latency per op:        0.008X ms
  Phase 3 (ECDSA + ZKP) Latency per op: 0.41XX ms
  Overhead Introduced for BFT Security: 0.40XX ms

  Estimated Max Verification TPS:
  Phase 2: ~120,XXX TPS
  Phase 3: ~2,4XX TPS
=========================================================
```
Performance Analysis

The following benchmarks were collected by averaging 1,000 cryptographic
verification cycles on a standard machine.
```
| Metric                   | Phase 2 (HMAC baseline) | Phase 3 (ECDSA + ZKP) | Analysis                                                     |
| :----------------------- | :---------------------- | :-------------------- | :----------------------------------------------------------- |
| Verification Latency     | 0.008 ms                | 0.412 ms              | Acceptable overhead for vastly superior asymmetric security. |
| Est. Max Throughput      | \~120,000 TPS           | \~2,400 TPS           | Remains highly competitive by avoiding global consensus.     |
| Local Update Latency     | O(1) (instant)          | O(1) (instant)        | Core "zero-latency" objective maintained.                    |
```
Roadmap for Phase 4 (Final Polish)

  - Docker Containerization: Wrap the SecureNode class into Docker containers to
    simulate a true distributed network.
  - Visualization Dashboard: Build a simple web-based UI with Flask/Socket.io to
    visualize the network state and Byzantine attacks in real-time.
  - Finalize IEEE Paper: Complete the "Results" and "Conclusion" sections using
    the collected benchmark data.

Authors

  - Syed Muhammad Ahmer | BSCS23167
  - Ahmed Nadeem | BSCS23185
  - Mashhood Shafqat | BSCS23188

Under the mentorship of Dr. Muhammad Umar Janjua.

References

This work is built upon the foundational research in CRDTs and distributed
systems:

1.  Shapiro, M., et al. (2011). Conflict-Free Replicated Data Types.
2.  Martin, H., et al. (2021). Byzantine Eventual Consistency and the
    Fundamental Limits of Peer-to-Peer Systems.
3.  Baquero, C., & Preguiça, N. (2016). Why Logical Clocks are Easy.

