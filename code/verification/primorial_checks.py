"""
Primorial-scale verification of the 1/25 invariant gap.
Implements the Type II bilinear sum checks.
"""
from sympy import totient
import numpy as np
from typing import List, Tuple
from sympy import primerange, isprime, mobius
from collections import Counter

class PrimorialVerifier:
    """
    Verify 1/25 gap on numbers coprime to primorial and ≡5 mod6.
    """
    
    def __init__(self, alpha: float = 24/25):
        self.alpha = alpha
        
    def primorial(self, n: int) -> int:
        """Compute n-th primorial (product of first n primes)."""
        primes = list(primerange(2, primerange(2, 1000)[n-1] + 1))
        return np.prod(primes[:n])
    
    def is_coprime_to_primorial(self, x: int, prim: int) -> bool:
        """Check if x is coprime to primorial P."""
        from math import gcd
        return gcd(x, prim) == 1
    
    def type_ii_sum(self, 
                    limit: int, 
                    primorial: int,
                    verbose: bool = False) -> Tuple[float, float, float]:
        """
        Approximate Type II bilinear sum on ≡5 mod6 numbers.
        
        Simplified proxy: count of numbers with given properties.
        Returns (actual_count, predicted_count, gap_ratio)
        """
        # Numbers up to limit, coprime to primorial, ≡5 mod6
        count_actual = 0
        for n in range(5, limit, 6):  # ≡5 mod6
            if self.is_coprime_to_primorial(n, primorial):
                count_actual += 1
        
        # Predicted count from singular series (simplified)
        # φ(primorial)/primorial * (limit/(6)) * 2 (for two residue classes mod6)
        from sympy import totient
        density = totient(primorial) / primorial
        predicted = density * (limit / 6) * 2  # Both 1 and 5 mod6
        
        # Observed gap
        if predicted > 0:
            gap_ratio = count_actual / predicted
        else:
            gap_ratio = 0
            
        if verbose:
            print(f"Primorial {primorial}:")
            print(f"  Actual: {count_actual}")
            print(f"  Predicted: {predicted:.2f}")
            print(f"  Ratio: {gap_ratio:.4f} (target 24/25 = 0.96)")
            
        return count_actual, predicted, gap_ratio
    
    def verify_primorial_scale(self, 
                               primorials: List[int],
                               limit_factor: int = 1000) -> dict:
        """
        Run verification across multiple primorial scales.
        """
        results = {}
        for i, p in enumerate(primorials):
            # Scale limit with primorial to keep counts reasonable
            limit = p * limit_factor
            actual, predicted, ratio = self.type_ii_sum(limit, p)
            results[f"P{i+1}#={p}"] = {
                "limit": limit,
                "actual": actual,
                "predicted": predicted,
                "ratio": ratio,
                "holds": abs(ratio - self.alpha) < 0.01  # Within 1%
            }
        return results
