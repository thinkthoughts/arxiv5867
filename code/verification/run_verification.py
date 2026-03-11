#!/usr/bin/env python3
"""
Run verification across the primorial scales from README.
"""

from primorial_checks import PrimorialVerifier
from sympy import primerange

def main():
    print("🔍 9423 Phase-Lock Invariant Verification\n")
    
    verifier = PrimorialVerifier(alpha=24/25)
    
    # First 16 primorials (matching README table)
    primes = list(primerange(2, 60))[:16]
    primorials = []
    current = 1
    for p in primes:
        current *= p
        primorials.append(current)
    
    print("Primorial | Size | Ratio | 1/25 Gap Holds?")
    print("-" * 50)
    
    results = verifier.verify_primorial_scale(primorials, limit_factor=1000)
    
    for name, data in results.items():
        holds = "✅" if data["holds"] else "❌"
        print(f"{name:10} | {data['limit']:8d} | {data['ratio']:.4f} | {holds}")
    
    # Summary
    all_hold = all(r["holds"] for r in results.values())
    print("\n" + "="*50)
    if all_hold:
        print("✅ Invariant confirmed: 1/25 gap holds across all scales.")
    else:
        print("⚠️  Invariant deviation detected at some scales.")

if __name__ == "__main__":
    main()
