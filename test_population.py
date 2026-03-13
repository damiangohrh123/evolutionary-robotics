import unittest
import population
import numpy as np

class TestPop(unittest.TestCase):
    
    def testSelPar(self):
        """Check that the selected parent ID is within the valid range (0-2)."""
        fits = [2.5, 1.2, 3.4]
        fitmap = population.Population.get_fitness_map(fits)
        pid = population.Population.select_parent(fitmap)
        
        # Ensure the index returned is a valid index for a list of 3 items
        self.assertLess(pid, 3)
        self.assertGreaterEqual(pid, 0)

    def testSelPar2(self):
        """
        Tests the 'Roulette Wheel' bias.
        With fitnesses [0, 1000, 0.1], the individual at index 1 
        holds >99.9% of the 'wheel' and should almost always be selected.
        """
        fits = [0, 1000, 0.1]
        fitmap = population.Population.get_fitness_map(fits)
        pid = population.Population.select_parent(fitmap)
        
        # In a deterministic sense for this test, index 1 is the only logical outcome
        self.assertEqual(pid, 1)     

if __name__ == "__main__":
    # Using exit=False allows the script to continue if you were running this 
    # as part of a larger test suite.
    unittest.main()