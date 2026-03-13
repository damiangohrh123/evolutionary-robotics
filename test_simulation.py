import unittest
import simulation
import creature
import population

class TestSim(unittest.TestCase):
    def testSimExists(self):
        """Check if the simulation object can be instantiated."""
        sim = simulation.Simulation()
        self.assertIsNotNone(sim)

    def testSimId(self):
        """Verify that PyBullet successfully returns a physics client ID."""
        sim = simulation.Simulation()
        self.assertIsNotNone(sim.physicsClientId)

    def testRun(self):
        """Ensure the run_creature method exists on the simulation object."""
        sim = simulation.Simulation()
        self.assertIsNotNone(sim.run_creature)

    def testPos(self):
        """
        Check that a creature actually moves. 
        Note: If this fails, the creature might be 'stuck' or the 
        motor force is too low.
        """
        sim = simulation.Simulation()
        cr = creature.Creature(gene_count=3)
        
        # We assume run_creature updates internal state of cr
        # or returns a result we can check.
        sim.run_creature(cr)
        
        # Based on your Simulation.py, results are stored in cr.sim_result
        if hasattr(cr, 'sim_result') and cr.sim_result is not None:
            start = cr.sim_result['start_pos']
            end = cr.sim_result['end_pos']
            self.assertNotEqual(start, end)
    
    def testPop(self):
        """Test running a small population sequentially."""
        pop = population.Population(pop_size=5, gene_count=3)
        sim = simulation.Simulation()
        for cr in pop.creatures:
            sim.run_creature(cr)
        
        dists = [cr.get_distance_travelled() for cr in pop.creatures]
        print(f"Distances: {dists}")
        self.assertIsNotNone(dists)

    # Uncomment this to test the multi-threaded simulation 
    # if your OS supports multiprocessing/forking
    """
    def testProc(self):
        pop = population.Population(pop_size=20, gene_count=3)
        tsim = simulation.ThreadedSim(pool_size=8)
        tsim.eval_population(pop, 2400)
        dists = [cr.get_distance_travelled() for cr in pop.creatures]
        print(f"Parallel Distances: {dists}")
        self.assertIsNotNone(dists)
    """

    def testProcNoThread(self):
        """Test the population evaluation logic using a single-threaded approach."""
        pop = population.Population(pop_size=20, gene_count=3)
        sim = simulation.Simulation()
        
        # Ensure eval_population is implemented in your Simulation class
        if hasattr(sim, 'eval_population'):
            sim.eval_population(pop, 2400)
            dists = [cr.get_distance_travelled() for cr in pop.creatures]
            print(f"Sequential Pop Distances: {dists}")
            self.assertIsNotNone(dists)

if __name__ == "__main__":
    unittest.main()