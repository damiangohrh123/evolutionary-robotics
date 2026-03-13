import pybullet as p
import pybullet_data
import os
import time
import numpy as np
import copy
import csv
import glob
import genome
import creature
import population
from simulation import ThreadedSim
from environment import setup_environment

def calculate_fitness(sim_result):
    if sim_result is None:
        return 0
    
    final_xy = sim_result['final_xy']
    final_z = sim_result['end_pos'][2]
    start_xy = sim_result['start_pos'][:2]
    mountain_top_xy = (0, 0)
    
    # Center Score
    dist_to_peak = float(np.linalg.norm(np.array(final_xy) - np.array(mountain_top_xy)))
    start_dist_to_peak = float(np.linalg.norm(np.array(start_xy) - np.array(mountain_top_xy)))
    
    if dist_to_peak >= start_dist_to_peak:
        center_score = 0  # If creature didn't move closer, fitness is 0
    else:
        center_score = (start_dist_to_peak - dist_to_peak) / start_dist_to_peak
        center_score = np.clip(center_score, 0, 1)
    
    # Height score
    peak_z = 5
    height_score = np.clip(final_z / peak_z, 0, 1)
    
    # Fitness score is center score multiplied by height score
    return center_score * height_score

def run_basic_ga():
    pool_size = 15
    pop_size = 50
    gene_count = 5
    mutation_rate = 0.4
    generations = 500
    
    print(f"  Population size: {pop_size}")
    print(f"  Gene count: {gene_count}")
    print(f"  Mutation rate: {mutation_rate}")
    print(f"  Generations: {generations}")
    
    # Use threaded sim for parallel simulations
    threaded_sim = ThreadedSim(pool_size=pool_size)

    # Create current population
    pop = population.Population(pop_size=pop_size, gene_count=gene_count)

    # Store metrics
    best_fitnesses = []
    average_fitnesses = []
    std_fitnesses = []
    best_ever_fitness = -float('inf')
    best_ever_creature = None

    # Main GA loop
    def ga_loop():
        nonlocal best_ever_fitness, best_ever_creature
        for gen in range(generations):
            print(f"\n Generation {gen+1}/{generations}")
            
            # Run parallel simulations
            threaded_sim.eval_population(pop, iterations=2400)
            
            fitnesses = []
            for i, cr in enumerate(pop.creatures):
                try:
                    sim_result = getattr(cr, 'sim_result', None)
                    fit = calculate_fitness(sim_result)
                except Exception as e:
                    print(f"[ERROR] Exception in fitness calculation for creature {i}: {e}")
                    fit = 0
                fitnesses.append(fit)

                # Update best ever
                if fit > best_ever_fitness:
                    best_ever_fitness = fit
                    best_ever_creature = copy.deepcopy(cr)
            
            # Stats calculation
            best_fit = max(fitnesses)
            avg_fit = np.mean(fitnesses)
            std_fit = np.std(fitnesses)
            
            best_fitnesses.append(best_fit)
            average_fitnesses.append(avg_fit)
            std_fitnesses.append(std_fit)
            
            print(f"  Generation {gen + 1}: Best = {best_fit:.2f}, Average = {avg_fit:.2f}")

            # Evolution Step
            fit_map = population.Population.get_fitness_map(fitnesses)
            new_creatures = []

            for _ in range(len(pop.creatures)):
                # Selection
                p1_ind = population.Population.select_parent(fit_map)
                p2_ind = population.Population.select_parent(fit_map)
                p1 = pop.creatures[p1_ind]
                p2 = pop.creatures[p2_ind]

                # Crossover and Mutation
                dna = genome.Genome.crossover(p1.dna, p2.dna)
                dna = genome.Genome.point_mutate(dna, rate=mutation_rate, amount=0.25)
                dna = genome.Genome.shrink_mutate(dna, rate=mutation_rate)
                dna = genome.Genome.grow_mutate(dna, rate=mutation_rate)
                
                new_cr = creature.Creature(1)
                new_cr.update_dna(dna)
                new_creatures.append(new_cr)

            # Elitism: Preserve the best creature
            for i, cr in enumerate(pop.creatures):
                if fitnesses[i] == best_fit:
                    elite = creature.Creature(1)
                    elite.update_dna(cr.dna)
                    new_creatures[0] = elite
                    print(f"  Elite creature preserved (fitness: {best_fit:.2f})")
                    break
            
            pop.creatures = new_creatures

    # Execute GA
    ga_loop()

    # File System Logic
    project_root = os.path.dirname(os.path.dirname(__file__))
    best_creatures_dir = os.path.join(project_root, 'best_creatures')
    experiments_dir = os.path.join(project_root, 'experiments')

    if best_ever_creature is not None:
        urdf_files = glob.glob(os.path.join(best_creatures_dir, 'best_creature*.urdf'))
        csv_files = glob.glob(os.path.join(best_creatures_dir, 'best_creature*.csv'))

        def extract_number(filename):
            basename = os.path.splitext(os.path.basename(filename))[0]
            if basename.startswith('best_creature'):
                num_str = basename[len('best_creature'):]
                return int(num_str) if num_str.isdigit() else 0
            return 0
        
        all_nums = [extract_number(f) for f in urdf_files + csv_files]
        next_num = max(all_nums + [0]) + 1

        # Save Best Creature
        urdf_name = os.path.join(best_creatures_dir, f'best_creature{next_num}.urdf')
        csv_name = os.path.join(best_creatures_dir, f'best_creature{next_num}.csv')
        
        with open(urdf_name, 'w') as f:
            f.write(best_ever_creature.to_xml())
        genome.Genome.to_csv(best_ever_creature.dna, csv_name)
    else:
        print("No valid creatures found in the entire run.")

    # Log Experiment Results
    existing_files = glob.glob(os.path.join(experiments_dir, 'experiment_run_*.csv'))
    run_numbers = []
    for f in existing_files:
        try:
            num_str = f.split('_')[-1].split('.')[0]
            if num_str.isdigit():
                run_numbers.append(int(num_str))
        except:
            continue

    run_id = max(run_numbers) + 1 if run_numbers else 1
    log_file = os.path.join(experiments_dir, f'experiment_run_{run_id}.csv')

    # Data Formatting
    best_fitnesses_clean = [round(float(fit), 4) for fit in best_fitnesses]
    average_fitnesses_clean = [round(float(fit), 4) for fit in average_fitnesses]
    std_fitnesses_clean = [round(float(fit), 4) for fit in std_fitnesses]

    with open(log_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Run ID', 'Population Size', 'Initial Genome Size', 'Mutation Rate', 'No. of Generations',
            'Best Fitness (Final Gen)', 'Average Fitness (Final Gen)', 'Std Dev Fitness (Final Gen)',
            'Best Fitness Progression', 'Average Fitness Progression', 'Std Dev Fitness Progression'
        ])
        writer.writerow([
            run_id, pop_size, gene_count, mutation_rate, generations,
            round(float(best_fitnesses[-1]), 4) if best_fitnesses else 0,
            round(float(average_fitnesses[-1]), 4) if average_fitnesses else 0,
            round(float(std_fitnesses[-1]), 4) if std_fitnesses else 0,
            best_fitnesses_clean, average_fitnesses_clean, std_fitnesses_clean
        ])

    # Final Cleanup
    for f in glob.glob('temp*.urdf'):
        try:
            os.remove(f)
        except:
            pass
            
    return best_fitnesses

if __name__ == '__main__':
    start_time = time.time()
    run_basic_ga()
    print(f"\nTotal Runtime: {time.time() - start_time:.2f} seconds")