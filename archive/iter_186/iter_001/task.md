Create a new file `src/fitness_functions.py` and implement a new fitness function called `CollisionFitness`.

This function must perform the following steps:
1.  Take a rule's truth table as input.
2.  Initialize a 128x128 hexagonal grid with a torus topology.
3.  Seed the grid with two 3-bit L-tromino particles placed on a direct, head-on collision course. For example, place one at (32, 64) and the other, rotated 180 degrees, at (96, 64). The initial total bit count must be 6.
4.  Run the simulation for 200 steps, which is sufficient time for the particles to meet and interact.
5.  The fitness score is defined as follows:
    - If `final_bit_count == initial_bit_count` (i.e., exactly 6), the fitness is 1.0.
    - If `final_bit_count != initial_bit_count`, the fitness is 0.0.

This function will serve as the core of a new evolutionary search for rules that exhibit elastic collisions. Add docstrings explaining its purpose and return value. Ensure it can be imported by other scripts.