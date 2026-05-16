Modify `src/fitness.py` to implement a new fitness function class named `RecessionBiasedFitness`.

This class should inherit from the existing `StagedCollisionFitness`. The core logic should be overridden as follows:

1.  Calculate the initial state (`initial_com1`, `initial_com2`, `initial_distance`, `initial_bits`).
2.  Run the simulation for the full duration.
3.  Calculate the final state (`final_com1`, `final_com2`, `final_distance`, `final_bits`).
4.  Determine if the 'approach' was successful, using the same logic as the parent class (i.e., the minimum distance during the simulation is less than a threshold). If not, return a fitness of 0.0.
5.  If the approach was successful, calculate the core fitness score:
    - `recession_score = final_distance / initial_distance`. This score should be capped at 1.0 (so `recession_score = min(1.0, final_distance / initial_distance)`).
    - `staged_score = 1.0 + recession_score` (This results in a value between 1.0 for fusion and 2.0 for perfect recession).
6.  Calculate the `bit_error = abs(initial_bits - final_bits)`.
7.  The final fitness score returned by the `__call__` method should be `staged_score / (1.0 + bit_error)`. This implements the "leaky" conservation principle from iter_192.

Add this new class to `src/fitness.py` and ensure it is importable. No other files need to be modified.