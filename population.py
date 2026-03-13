import creature
import numpy as np

class Population:
    def __init__(self, pop_size, gene_count, motor_amplitude=None, motor_speed=None):
        # Standardized the list comprehension for creating the population
        self.creatures = [
            creature.Creature(
                gene_count=gene_count, 
                motor_amplitude=motor_amplitude, 
                motor_speed=motor_speed
            ) for i in range(pop_size)
        ]

    @staticmethod
    def get_fitness_map(fits):
        """Creates a cumulative fitness map (prefix sums) for selection."""
        fitmap = []
        total = 0
        for f in fits:
            total = total + f
            fitmap.append(total)
        return fitmap
    
    @staticmethod
    def select_parent(fitmap):
        """
        Selects an individual based on the fitness map using 
        Roulette Wheel Selection.
        """
        if not fitmap or fitmap[-1] == 0:
            # Handle edge case where all fitness is zero
            return np.random.randint(0, len(fitmap)) if fitmap else 0
            
        r = np.random.rand()  # Random float between 0 and 1
        r = r * fitmap[-1]    # Scale random number to the total fitness sum
        
        for i in range(len(fitmap)):
            if r <= fitmap[i]:
                return i
        
        # Fallback: if not found due to rounding, return last index
        return len(fitmap) - 1