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
        iterations = 1000
        
        pop = population.Population(pop_size=pop_size, gene_count=gene_count)
        
        # Single-threaded simulation instance
        sim = simulation.Simulation()

        for gen in range(iterations):
            # Non-threaded evaluation: process creatures one at a time
            for cr in pop.creatures: 
                sim.run_creature(cr, 2400)             
            
            # Extract metrics
            fits = [cr.get_distance_travelled() for cr in pop.creatures]
            links = [len(cr.get_expanded_links()) for cr in pop.creatures]
            
            # Cleaned up progress reporting
            print(f"Gen {gen} | "
                  f"Fittest: {np.round(np.max(fits), 3)} | "
                  f"Mean: {np.round(np.mean(fits), 3)} | "
                  f"Mean Links: {np.round(np.mean(links))} | "
                  f"Max Links: {np.round(np.max(links))}")       

            # Evolution Step
            fit_map = population.Population.get_fitness_map(fits)
            new_creatures = []
            
            for i in range(len(pop.creatures)):
                # Roulette wheel selection
                p1_ind = population.Population.select_parent(fit_map)
                p2_ind = population.Population.select_parent(fit_map)
                p1 = pop.creatures[p1_ind]
                p2 = pop.creatures[p2_ind]
                
                # Crossover and various mutation types
                dna = genome.Genome.crossover(p1.dna, p2.dna)
                dna = genome.Genome.point_mutate(dna, rate=0.1, amount=0.25)
                dna = genome.Genome.shrink_mutate(dna, rate=0.25)
                dna = genome.Genome.grow_mutate(dna, rate=0.1)
                
                cr_child = creature.Creature(1)
                cr_child.update_dna(dna)
                new_creatures.append(cr_child)
            
            # Elitism: Ensure the best performer survives to the next generation
            max_fit = np.max(fits)
            for cr in pop.creatures:
                if cr.get_distance_travelled() == max_fit:
                    new_cr = creature.Creature(1)
                    new_cr.update_dna(cr.dna)
                    # Replace first child with the elite parent
                    new_creatures[0] = new_cr 
                    
                    # Save the elite DNA for later playback
                    filename = f"elite_{gen}.csv"
                    genome.Genome.to_csv(cr.dna, filename)
                    break 
            
            pop.creatures = new_creatures
                            
        self.assertNotEqual(fits[0], 0)

if __name__ == "__main__":
    unittest.main()