# metrics_v3.py
# Phase 3: Benchmarking and Performance Metrics

import time
from crypto_zkp import CryptoManager, MonotonicZKP
import hmac, hashlib, json

def benchmark_crypto(runs=1000):
    print("=" * 55)
    print("  Phase 3 Performance Benchmarks (1000 Iterations)")
    print("=" * 55)

    data = {"test": "payload", "value": 12345}
    
    # --- PHASE 2: HMAC (Baseline) ---
    hmac_key = b"secret_shared_key_123"
    
    start = time.perf_counter()
    for _ in range(runs):
        data_bytes = json.dumps(data, sort_keys=True).encode()
        sig = hmac.new(hmac_key, data_bytes, hashlib.sha256).hexdigest()
        # Verify
        valid = hmac.compare_digest(sig, hmac.new(hmac_key, data_bytes, hashlib.sha256).hexdigest())
    end = time.perf_counter()
    hmac_time_ms = ((end - start) / runs) * 1000

    # --- PHASE 3: ECDSA + ZKP Simulation ---
    priv, pub = CryptoManager.generate_keys()
    
    start = time.perf_counter()
    for _ in range(runs):
        # 1. Sign
        sig = CryptoManager.sign_data(priv, data)
        # 2. ZKP Gen
        zkp = MonotonicZKP.generate_proof(0, 10, "sim_key")
        
        # 3. Verify
        is_sig = CryptoManager.verify_signature(pub, data, sig)
        is_zk = MonotonicZKP.verify_proof(0, 10, zkp, "sim_key")
    end = time.perf_counter()
    ecdsa_time_ms = ((end - start) / runs) * 1000

    print(f"  Phase 2 (HMAC) Latency per op:        {hmac_time_ms:.4f} ms")
    print(f"  Phase 3 (ECDSA + ZKP) Latency per op: {ecdsa_time_ms:.4f} ms")
    print(f"  Overhead Introduced for BFT Security: {(ecdsa_time_ms - hmac_time_ms):.4f} ms")
    
    # Estimated TPS based on latency
    tps_p2 = 1000 / hmac_time_ms if hmac_time_ms > 0 else 0
    tps_p3 = 1000 / ecdsa_time_ms if ecdsa_time_ms > 0 else 0
    
    print(f"\n  Estimated Max Verification TPS:")
    print(f"  Phase 2: ~{int(tps_p2):,} TPS")
    print(f"  Phase 3: ~{int(tps_p3):,} TPS")
    print("=" * 55)

if __name__ == "__main__":
    benchmark_crypto()
