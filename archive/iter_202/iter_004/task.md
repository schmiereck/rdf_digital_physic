**Context:** After two successive failures (`202.2`, `202.3`), we have now developed and validated `RobustCumulativeDisplacementFitness`, a function confirmed to be immune to both the phase-sampling and annihilation exploits. The path is finally clear to conduct a legitimate search for a `v<c` glider.

**Goal:** Evolve a rule that produces a stable, bit-conserving, `v<c` (sub-light speed) glider using the new, robust fitness function.

**Task:**
1.  Configure and run an evolutionary search using the `src/main_v2.py` script.
2.  **Use the `RobustCumulativeDisplacementFitness` function** validated in `202.3`.
3.  Use the standard evolutionary parameters:
    *   Seed Particle: 3-bit L-Tromino
    *   Grid Size: 128x128 Torus
    *   Population Size: 100 rules
    *   Elite Anteil: 10%
4.  Run the evolution for **20 generations**.
5.  Identify the champion rule and save it to `archive/iter_202/results/champion_rule.json`.
6.  Perform a brief, final validation on the champion rule:
    *   Run it for 512 steps.
    *   Confirm its final fitness score.
    *   Generate a GIF visualization (`champion.gif`).
7.  Write a summary of the run, including final fitness, number of generations, and qualitative observations from the GIF, to `archive/iter_202/results/evolution_summary.txt`.