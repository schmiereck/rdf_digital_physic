**Context:** The `CumulativeDisplacementFitness` function (iter_202.1) fixed the phase-sampling exploit but was shown to be vulnerable to an annihilation exploit (iter_202.2). We need to create a new function that is robust to both.

**Task:**
1.  Go to `src/fitness_v2.py`.
2.  Create a new class, `RobustCumulativeDisplacementFitness`, that inherits from `CumulativeDisplacementFitness`.
3.  Override the `evaluate` method. The new method must implement a "conservation gate":
    *   First, it must check if `final_bit_count` is exactly equal to `initial_bit_count`.
    *   If they are not equal, the function must immediately return a fitness score of `0.0`.
    *   If they are equal, it should call the parent class's `evaluate` method (`super().evaluate(...)`) to calculate and return the fitness based on displacement.
4.  Update `src/main_v2.py` to make this new `RobustCumulativeDisplacementFitness` function available via the `--fitness` command-line argument.
5.  **Validate the fix against both known exploits:**
    a.  Run a simulation with the **annihilating rule** discovered in `iter_202.2`. (The rule is in the sub-iteration `archive/iter_202.2/iter_001/results/champion_rule_gen15.json`).
    b.  Run a simulation with the **stationary oscillator rule** from `iter_200.1`. (The rule is at `archive/iter_200.1/results/champion_v_lt_c_rule.json`).
6.  **Success Criteria:**
    *   The fitness for the annihilating rule must be exactly `0.0`.
    *   The fitness for the stationary oscillator must be less than `0.2`.
7.  Report both validation fitness scores in the result metrics. Create a report file at `archive/iter_202/results/robust_validation_report.txt`.