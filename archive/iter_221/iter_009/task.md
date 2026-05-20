Create a python script src/run_evolution_exp_221_warm.py. It should be a modification of src/run_evolution_exp_220_fixed.py.
Specifically:
1. Load 100 chromosomes from 'archive/iter_215/results/final_population.json' to initialize the population.
2. Configure the fitness function using DisplacementConsistencyFitness with max_bit_threshold=12 and max_velocity_threshold=0.9, simulating for 500 steps.
3. Run the Genetic Algorithm for 20 generations.
4. Save the results (evolution_summary.csv, champion_vc_rule.json, and champion_vc_glider.gif) to 'archive/iter_221/results/'.
5. Execute the script to complete the evolution and save the outputs. Do not print too much output to avoid token limits.