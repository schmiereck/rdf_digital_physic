Based on the findings from iter_203, create a new, more robust fitness function to guide the evolutionary search for a v<c glider.

1.  **Create a new file:** `src/fitness_functions.py`.
2.  **Implement `NetDisplacementFitness`:** Inside the new file, create a class `NetDisplacementFitness`.
    - It should calculate fitness based on the **net displacement** of the particle's center of mass (Euclidean distance between the start and end points of the simulation). This is the key change to defeat the 'compact oscillator' exploit.
    - It must also incorporate a penalty for the final bounding box size (`final_bb_area`) to retain the defense against the 'puffer' exploit.
    - The formula should be `fitness = net_displacement / (1 + final_bb_area)`.
    - It should also include bit conservation checks from `RobustCumulativeDisplacementFitness`. If the initial and final bit counts do not match the seed's bit count (3 bits for the L-tromino), the fitness must be 0.
3.  **Update `run_vc_search.py`:** Modify the main evolutionary search script `src/run_vc_search.py` to import and use this new `NetDisplacementFitness` class instead of the old one.