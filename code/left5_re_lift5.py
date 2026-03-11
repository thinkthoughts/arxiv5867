"""
Left5-Re-Lift5: 9423 Phase-Locked Sampling

Implements the core invariant-preserving sampler:
α·softmax + (1-α)·uniform with 9423 cyclic filtering.
α = 24/25 (coherence), 1-α = 1/25 (freedom).
"""

import numpy as np
import hashlib
from typing import Dict, List, Optional, Union

class Left5ReLift5:
    """
    9423 phase-locked sampler preserving exact 1/25 variance floor.
    
    Attributes:
        alpha: Coherence weight (default 24/25)
        cycle: 9423 cycle classes [9,4,2,3]
        mod: Hash modulus for token classification
    """
    
    def __init__(self, alpha: float = 24/25, mod: int = 20):
        self.alpha = float(alpha)
        self.cycle = [9, 4, 2, 3]
        self.mod = mod
        self._validate_parameters()
    
    def _validate_parameters(self):
        """Ensure alpha is in valid range."""
        if not 0 <= self.alpha <= 1:
            raise ValueError(f"alpha must be between 0 and 1, got {self.alpha}")
    
    def _token_class(self, token: Union[str, int]) -> int:
        """
        Deterministic hash-based class assignment.
        
        Args:
            token: Token identifier (string or integer)
            
        Returns:
            Integer class in [0, mod-1]
        """
        if isinstance(token, int):
            token = str(token)
        h = hashlib.sha256(token.encode('utf-8')).hexdigest()
        return int(h[:8], 16) % self.mod
    
    def filter_by_cycle(self, tokens: List[Union[str, int]], step: int) -> List[Union[str, int]]:
        """
        Filter tokens by 9423 cycle class at given step.
        
        Args:
            tokens: List of token identifiers
            step: Current generation step (0-indexed)
            
        Returns:
            Filtered list of admissible tokens
        """
        allowed_class = self.cycle[step % len(self.cycle)]
        return [t for t in tokens if self._token_class(t) == allowed_class]
    
    def softmax(self, logits: np.ndarray) -> np.ndarray:
        """
        Numerically stable softmax.
        
        Args:
            logits: Raw score array
            
        Returns:
            Probability distribution
        """
        logits = logits - np.max(logits)  # Stability
        exp_logits = np.exp(logits)
        return exp_logits / np.sum(exp_logits)
    
    def sample(self, 
               scores: Dict[Union[str, int], float], 
               step: int,
               temperature: float = 1.0) -> Optional[Union[str, int]]:
        """
        Sample a token using 9423 phase-locked mixture.
        
        Args:
            scores: Dictionary mapping tokens to logits/scores
            step: Current generation step
            temperature: Sampling temperature (applied to logits)
            
        Returns:
            Selected token, or None if no admissible tokens
        """
        # Step 1: Filter by 9423 cycle
        tokens = list(scores.keys())
        admissible = self.filter_by_cycle(tokens, step)
        
        if not admissible:
            return None
        
        # Step 2: Extract and adjust logits
        logits = np.array([scores[t] for t in admissible])
        logits = logits / temperature
        
        # Step 3: Coherence component (softmax)
        coherence_probs = self.softmax(logits)
        
        # Step 4: Freedom component (uniform)
        uniform_prob = 1.0 / len(admissible)
        
        # Step 5: Mix according to alpha
        final_probs = self.alpha * coherence_probs + (1 - self.alpha) * uniform_prob
        
        # Step 6: Sample
        return np.random.choice(admissible, p=final_probs)
    
    def get_probabilities(self,
                         scores: Dict[Union[str, int], float],
                         step: int,
                         temperature: float = 1.0) -> Optional[Dict[Union[str, int], float]]:
        """
        Return full probability distribution over admissible tokens.
        
        Useful for analysis and debugging.
        """
        tokens = list(scores.keys())
        admissible = self.filter_by_cycle(tokens, step)
        
        if not admissible:
            return None
        
        logits = np.array([scores[t] for t in admissible]) / temperature
        coherence_probs = self.softmax(logits)
        uniform_prob = 1.0 / len(admissible)
        final_probs = self.alpha * coherence_probs + (1 - self.alpha) * uniform_prob
        
        return dict(zip(admissible, final_probs))
