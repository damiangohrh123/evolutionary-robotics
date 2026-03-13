#!/usr/bin/env python3
"""
Quick Start Script for Mountain Climbing Genetic Algorithm
This script provides a simple way to test the system and see results quickly.
"""

import sys
import os

# Ensure the script can find local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def quick_demo():
    """Run a quick demonstration of the mountain climbing GA."""
    print("=" * 60)
    print("MOUNTAIN CLIMBING GENETIC ALGORITHM - QUICK DEMO")
    print("=" * 60)
    
    print("\nThis demo will:")
    print("1. Create a simple creature")
    print("2. Show its genetic encoding")
    print("3. Generate its URDF representation")
    print("4. Run a quick evolution simulation")
    
    try:
        import creature
        import genome
        import population
        import numpy as np
        
        print("\n✓ All required modules imported successfully")
        
        # 1. Create a simple creature
        print("\n1. Creating a simple creature...")
        cr = creature.Creature(gene_count=3)
        print(f"   Creature created with {len(cr.dna)} genes")
        
        # 2. Show genetic encoding
        print("\n2. Genetic encoding:")
        spec = genome.Genome.get_gene_spec()
        for i, gene in enumerate(cr.dna):
            gdict = genome.Genome.get_gene_dict(gene, spec)
            print(f"   Gene {i+1}: length={gdict['link-length']:.2f}, radius={gdict['link-radius']:.2f}")
        
        # 3. Generate URDF
        print("\n3. Generating URDF representation...")
        xml = cr.to_xml()
        print(f"   URDF generated ({len(xml)} characters)")
        
        # 4. Create a small population
        print("\n4. Creating population for evolution...")
        pop = population.Population(pop_size=5, gene_count=3)
        print(f"   Population created with {len(pop.creatures)} creatures")
        
        # 5. Simulate a few generations
        print("\n5. Running quick evolution simulation...")
        for gen in range(3):
            # Mock fitness evaluation
            fitnesses = [np.random.random() * 100 for _ in range(len(pop.creatures))]
            best_fit = max(fitnesses)
            avg_fit = np.mean(fitnesses)
            print(f"   Generation {gen+1}: best={best_fit:.1f}, avg={avg_fit:.1f}")
            
            # Simple selection and reproduction
            fit_map = population.Population.get_fitness_map(fitnesses)
            new_creatures = []
            for _ in range(len(pop.creatures)):
                p1_ind = population.Population.select_parent(fit_map)
                p2_ind = population.Population.select_parent(fit_map)
                
                p1 = pop.creatures[p1_ind]
                p2 = pop.creatures[p2_ind]
                
                dna = genome.Genome.crossover(p1.dna, p2.dna)
                dna = genome.Genome.point_mutate(dna, rate=0.1, amount=0.25)
                
                new_cr = creature.Creature(1)
                new_cr.update_dna(dna)
                new_creatures.append(new_cr)
            
            pop.creatures = new_creatures
        
        print("\n✓ Quick demo completed successfully!")
        print("\nNext steps:")
        print("1. Install PyBullet: pip install pybullet")
        print("2. Run full simulation: python mountain_climbing_ga.py")
        print("3. Run parameter experiments: python mountain_climbing_ga.py")
        print("4. Run encoding experiments: python advanced_encoding_experiments.py")
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Please install required packages:")
        print("pip install pybullet numpy matplotlib")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your installation and try again.")

def show_help():
    """Show help information."""
    print("=" * 60)
    print("MOUNTAIN CLIMBING GA - HELP")
    print("=" * 60)
    
    print("\nAvailable scripts:")
    print("1. quick_start.py                  - This demo script")
    print("2. mountain_climbing_ga.py         - Full GA with experiments")
    print("3. advanced_encoding_experiments.py - Advanced encoding schemes")
    print("4. test_mountain_climbing.py       - Test suite")
    print("5. cw-envt.py                      - Original coursework environment")
    
    print("\nQuick commands:")
    print("python quick_start.py                    # Run this demo")
    print("python mountain_climbing_ga.py           # Run full GA")
    print("python advanced_encoding_experiments.py  # Run encoding experiments")
    
    print("\nInstallation:")
    print("pip install -r requirements.txt")
    print("python quick_start.py")

if __name__ == "__main__":
    # Check for help flags
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['-h', '--help', 'help']:
        show_help()
    else:
        quick_demo()