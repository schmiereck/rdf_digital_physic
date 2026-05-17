Using the champion elastic collision rule from `archive/iter_193/iter_002/results/champion_rule.json`, simulate a collision between two standard L-tromino gliders at a 60-degree angle. The gliders should be positioned to collide near the center of a 256x256 grid. Run the simulation for at least 500 steps to observe the full interaction.

The primary goal is to determine if the collision is elastic and bit-conserving, and to characterize the scattering.

**Tasks:**
1.  Load the champion rule.
2.  Set up the initial grid with two gliders on a 60-degree collision course.
3.  Run the simulation for 500+ steps.
4.  Analyze the outcome:
    - Was the total bit count conserved throughout the interaction?
    - Did the gliders survive the collision?
    - What were the exit angles and velocities?
5.  Save the simulation as a GIF to `archive/iter_197/results/collision_60_degree.gif`.
6.  Report the findings in the result.
