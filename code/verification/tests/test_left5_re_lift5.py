"""
Unit tests for Left5ReLift5 sampler.
"""

import unittest
import numpy as np
from code.left5_re_lift5 import Left5ReLift5

class TestLeft5ReLift5(unittest.TestCase):
    
    def setUp(self):
        self.sampler = Left5ReLift5(alpha=24/25)
        self.test_scores = {
            "A": 2.0,
            "B": 1.5,
            "C": 0.5,
            "D": -1.0,
            "E": 3.0,
        }
    
    def test_initialization(self):
        self.assertEqual(self.sampler.alpha, 24/25)
        self.assertEqual(self.sampler.cycle, [9, 4, 2, 3])
        
    def test_token_class_consistency(self):
        """Same token always gets same class."""
        token = "test_token"
        class1 = self.sampler._token_class(token)
        class2 = self.sampler._token_class(token)
        self.assertEqual(class1, class2)
    
    def test_filter_by_cycle(self):
        tokens = ["A", "B", "C", "D", "E"]
        # At step 0, class 9 should be allowed
        filtered = self.sampler.filter_by_cycle(tokens, 0)
        # Verify all returned tokens have class 9
        for t in filtered:
            self.assertEqual(self.sampler._token_class(t) % 20, 9)
    
    def test_softmax_properties(self):
        logits = np.array([1.0, 2.0, 3.0])
        probs = self.sampler.softmax(logits)
        self.assertAlmostEqual(np.sum(probs), 1.0)
        self.assertTrue(np.all(probs >= 0))
    
    def test_sample_with_no_admissible(self):
        # Step where no tokens match the allowed class
        result = self.sampler.sample(self.test_scores, step=999)
        self.assertIsNone(result)
    
    def test_probabilities_sum_to_one(self):
        probs_dict = self.sampler.get_probabilities(self.test_scores, step=0)
        if probs_dict:
            self.assertAlmostEqual(sum(probs_dict.values()), 1.0)

if __name__ == '__main__':
    unittest.main()
