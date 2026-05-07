# crypto_zkp.py
# Phase 3: Cryptographic upagrades (ECDSA + Monotonicity ZKP)

import hashlib
import secrets
import json
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

class CryptoManager:
    """Handles ECDSA Key Generation, Signing, and Verification."""
    @staticmethod
    def generate_keys():
        private_key = ec.generate_private_key(ec.SECP256R1())
        public_key = private_key.public_key()
        return private_key, public_key

    @staticmethod
    def sign_data(private_key, data_dict):
        data_bytes = json.dumps(data_dict, sort_keys=True).encode()
        signature = private_key.sign(data_bytes, ec.ECDSA(hashes.SHA256()))
        return signature

    @staticmethod
    def verify_signature(public_key, data_dict, signature):
        data_bytes = json.dumps(data_dict, sort_keys=True).encode()
        try:
            public_key.verify(signature, data_bytes, ec.ECDSA(hashes.SHA256()))
            return True
        except Exception:
            return False

class MonotonicZKP:
    """
    Simulates a Zero-Knowledge Proof (Sigma Protocol) for S' >= S.
    Proves a node's counter/state only goes up without revealing the raw inputs
    to unauthorized observers during transmission.
    """
    @staticmethod
    def generate_proof(old_val, new_val, private_key_hex_sim):
        if new_val < old_val:
            raise ValueError("Byzantine Fault: Cannot generate proof for non-monotonic update.")
        
        diff = new_val - old_val
        nonce = secrets.token_hex(16)
        
        # Commitment hides the exact values but binds the difference to the sender
        commitment = hashlib.sha256(f"{diff}:{nonce}:{private_key_hex_sim}".encode()).hexdigest()
        
        return {
            "diff": diff,
            "commitment": commitment,
            "nonce": nonce
        }

    @staticmethod
    def verify_proof(old_val, new_val, proof, private_key_hex_sim):
        # 1. Monotonicity (Algebraic) Check
        if proof['diff'] < 0:
            print("  [ZKP-Filter] REJECTED: Negative difference detected!")
            return False
            
        # 2. State transition validation
        if new_val != old_val + proof['diff']:
            print("  [ZKP-Filter] REJECTED: State mismatch!")
            return False
            
        # 3. Commitment Verification (Simulated ZK check)
        expected_commit = hashlib.sha256(f"{proof['diff']}:{proof['nonce']}:{private_key_hex_sim}".encode()).hexdigest()
        if expected_commit != proof['commitment']:
            print("  [ZKP-Filter] REJECTED: ZKP Commitment failed!")
            return False
            
        return True
