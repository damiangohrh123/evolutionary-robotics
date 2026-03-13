# NOTE: If you are on a Windows machine or an M1 Mac, this version 
# may not work due to multiprocessing limitations. 
# Use test_ga_single_thread.py instead if you encounter errors.

import unittest
import population
import simulation
import genome
import creature
import numpy as np

class TestGA(unittest.TestCase):
    def testBasicGA(self):
        # Configuration
        pop_size = 10
        gene_count = 3
        generations = 1000
        
        # Initialize population
        pop = population.Population(pop_size=pop_size, gene_count=gene_count)
        
        # Initialize multi-threaded simulation pool
        sim = simulation.ThreadedSim(pool_size=4) # Adjusted pool_size for parallel work

        for iteration in range(generations):
            # Parallel evaluation of the entire population
            sim.eval_population(pop, 2400) 
            
            # Extract fitness and morphology metrics
            fits = [cr.get_distance_travelled() for cr in pop.creatures]
            links = [len(cr.get_expanded_links()) for cr in pop.creatures]
            
            # Formatted progress reporting
            print(f"Gen {iteration} | "
                  f"Fittest: {np.round(np.max(fits), 3)} | "
                  f"Mean: {np.round(np.mean(fits), 3)} | "
                  f"Mean Links: {np.round(np.mean(links))} | "
                  f"Max Links: {np.round(np.max(links))}")       

            # Evolution Step
            fit_map = population.Population.get_fitness_map(fits)
            new_creatures = []
            
            for i in range(len(pop.creatures)):
                # Parent Selection
                p1_ind = population.Population.select_parent(fit_map)
                p2_ind = population.Population.select_parent(fit_map)
                p1 = pop.creatures[p1_ind]
                p2 = pop.creatures[p2_ind]
                
                # Crossover and Mutation sequence
                dna = genome.Genome.crossover(p1.dna, p2.dna)
                dna = genome.Genome.point_mutate(dna, rate=0.1, amount=0.25)
                dna = genome.Genome.shrink_mutate(dna, rate=0.25)
                dna = genome.Genome.grow_mutate(dna, rate=0.1)
                
                # Create child
                child = creature.Creature(1)
                child.update_dna(dna)
                new_creatures.append(child)
            
            # Elitism: Preserve the best performer
            max_fit = np.max(fits)
            for cr in pop.creatures:
                if cr.get_distance_travelled() == max_fit:
                    elite_cr = creature.Creature(1)
                    elite_cr.update_dna(cr.dna)
                    
                    # Place elite at index 0
                    new_creatures[0] = elite_cr
                    
                    # Save DNA to CSV for future analysis
                    filename = f"elite_{iteration}.csv"
                    genome.Genome.to_csv(cr.dna, filename)
                    break 
            
            # Advance to the next generation
            pop.creatures = new_creatures
                            
        self.assertNotEqual(fits[0], 0)

if __name__ == "__main__":
    unittest.main()