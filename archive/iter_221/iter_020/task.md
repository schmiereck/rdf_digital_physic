Write a python script that:
1. Loads the champion rule 'archive/iter_221/results/champion_vc_rule.json'.
2. Simulates the L-tromino seed with this rule on a 128x128 grid for 500 steps, recording the history.
3. Instantiates DisplacementConsistencyFitness with num_windows=5, max_bit_threshold=12, max_velocity_threshold=0.9.
4. Evaluates the history, and prints out the exact intermediate calculations: 'mean_velocity_magnitude', 'std_dev_velocity_magnitudes', and the leaky bit conservation score.
Execute the script and print the output. Do not output yaml block.