Write a python script to characterize the champion rule from 'archive/iter_221/results/champion_vc_rule.json'.
Specifically:
1. Load the rule dictionary from the JSON file.
2. Initialize a 128x128 grid with the L-tromino seed.
3. Simulate it for 500 steps.
4. For each step, record the step number, the active cell count (bit count), and the unwrapped center of mass coordinates (row, col) using unwrapped tracking.
5. Compute the net displacement (Euclidean distance between CoM at step 0 and step 500).
6. Compute the average speed (cells per step).
7. Print out the trajectory details: the bit count at each 50 steps, the final displacement, and the average speed.
8. Write these results to 'archive/iter_221/results/trajectory_analysis.txt'.
Execute the script and print the output to stdout.