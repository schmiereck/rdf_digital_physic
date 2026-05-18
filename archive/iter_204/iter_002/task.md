Create a validation script `src/validate_net_fitness.py` to test the new `NetDisplacementFitness` function against the known exploits from `iter_203`.

**Script Logic:**

1.  **Load Exploit Rules:**
    -   Load the "puffer" champion rule. You can likely find this in `archive/iter_203/iter_002/results/champion_rule.json`.
    -   Load the "compact oscillator" champion rule. This should be in `archive/iter_203/iter_003/results/champion_rule.json`.
    -   Handle the case where these files might not exist gracefully.

2.  **Instantiate Fitness Function:**
    -   Create an instance of `NetDisplacementFitness` from `src/fitness_functions.py`.

3.  **Evaluate and Report:**
    -   For each of the two exploit rules:
        -   Calculate the fitness using the new function.
        -   Print the rule name (puffer/oscillator), the calculated fitness score, and the key metrics: `net_displacement`, `final_bb_area`, and `final_bits`.

**Success Criterion:**
The script's output must show that both exploit rules receive a fitness score near 0.0, confirming the new fitness function correctly rejects them. Execute the script after creating it.