Create and run a python script src/analyze_collision_dynamics.py to analyze the final states of the sub-light glider collisions at step 200 for offsets -4 to +4.
The script should:
1. Load champion_rule_perfect.json and convert to LUT.
2. For each offset in range(-4, 5):
   - Initialize the collision grid (just like in src/test_vc_collision.py).
   - Simulate for 200 steps, recording the grid at step 190 and step 200.
   - Analyze whether the 8 bits at the end are:
     a) Two independent moving gliders (do they move between step 190 and 200?). If they move, are they the original gliders moving in NW and SE directions, or did their trajectories change?
     b) A single 8-bit stationary still life or oscillator (no net motion).
     c) Chaotic / annihilated / other.
3. Save the detailed findings to archive/iter_223/results/collision_dynamics_analysis.json.
4. Print a clean, readable text summary of the physical classification of each offset's collision.