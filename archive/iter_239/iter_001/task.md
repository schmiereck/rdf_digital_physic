You are an elite scientific executor agent. Your goal for this sub-task is to write/overwrite `src/pre_registration.md` and then implement and run the 2D hexagonal CA collision sweep script `src/run_scattering_sweep.py`.

Follow these instructions strictly:

1. PRE-REGISTRATION FIRST:
Overwrite `src/pre_registration.md` to pre-register Path A: Classical Soliton Scattering Characterization.
The pre-registration MUST follow this structure:
- Working Hypothesis: Under the v=0.469c sub-light glider rule ('champion_rule_perfect.json'), the collision of two gliders exhibits classical soliton-like phase-dependent scattering and annihilation. The collision outcome (Annihilation, Transmission, Scattering/Deflection, Chaotic explosion) is a non-linear, deterministic function of both the relative transverse offset \Delta y and the relative temporal phase delay \Delta t. The boundaries between these outcome regimes in the (\Delta y, \Delta t) phase space vary periodically with \Delta t, reflecting the periodic internal state cycle of the gliders.
- Protocol:
  * Grid: 256x256 grid to prevent any toroidal wrapping artifacts over 200 steps of simulation.
  * Glider Rule: 'archive/iter_222/results/champion_rule_perfect.json'.
  * Initial conditions: Glider A launched from (160, 96) moving NW, Glider B launched from (96 + \Delta y, 160 + \Delta y) moving SE with a temporal phase delay of \Delta t steps (meaning Glider B is advanced or delayed in its internal step cycle, or its launch is delayed by \Delta t steps. Let's implement temporal delay simply by delaying the launch of Glider B by \Delta t steps, or by running Glider B individually for \Delta t steps before placing it on the joint grid. Running it individually for \Delta t steps and then placing it on the grid is better, as it preserves the exact distance and relative arrival time, or simply delaying the launch is fine. Let's do: launch Glider A at t=0, and launch Glider B at t=\Delta t steps, or advance Glider B's state by \Delta t steps at t=0. Actually, advancing Glider B's state by \Delta t steps and shifting its position backwards by v * \Delta t to ensure they still meet at the exact same location is elegant, but simply starting Glider A at (160, 96) and Glider B at (96 + \Delta y, 160 + \Delta y) and letting Glider B be delayed in time (e.g., launched at t = \Delta t) is also extremely standard and simple!). Let's use the delayed-launch method: Glider A is placed at t=0; Glider B is placed at t=\Delta t; both run. Wait, to make sure they still collide, if Glider B is delayed by \Delta t steps, its initial position can be shifted closer to the collision center by v * \Delta t, or we can just keep the positions fixed and let them collide with a slight asymmetry. Since the speed is ~0.469, a delay of \Delta t steps means they meet slightly shifted from the center. This is perfectly fine!
  * Sweep ranges: \Delta y \in [-4, 4] (integer steps) and \Delta t \in [0, 12] (integer steps), yielding 9 * 13 = 117 configurations.
  * For each configuration, run the active simulation (both gliders) for 200 steps, and run independent control simulations for Glider A and Glider B.
- Falsification Criterion:
  * The hypothesis of phase-dependent soliton scattering is refuted if the collision outcome classification (Annihilation, Deflection, Transmission, Chaos) is invariant under temporal phase shifts \Delta t (i.e. changing \Delta t has no effect on the outcome for all \Delta y).
  * The hypothesis is refuted if the active joint state is a trivial linear superposition (bitwise OR) of the single-glider control states across all configurations.
  * The hypothesis is refuted if the interaction cross-section does not show periodic structures with \Delta t.

2. IMPLEMENT THE SWEEPER SCRIPT `src/run_scattering_sweep.py`:
- Load the champion rule from `archive/iter_222/results/champion_rule_perfect.json`.
- Set up a 2D hex CA simulation using the LUT. Use the hex stepping function from `src/analyze_collision_dynamics.py` but on a 256x256 grid.
- Implement a simulation loop for:
  * Active run: both gliders are simulated together. Glider A starts at (160, 96). Glider B starts at (96 + \Delta y, 160 + \Delta y). Glider B's launch is delayed by \Delta t steps, meaning we only place the 3 bits of Glider B on the grid at step \Delta t.
  * Control A run: only Glider A is simulated.
  * Control B run: only Glider B is simulated (placed at step \Delta t).
- Classify the outcome of the Active run at step 200 into:
  * "Annihilation": final bit count on the grid is exactly 0.
  * "Transmission": both gliders survive and continue in their original directions without path deviation or bit change (e.g., final bit count is exactly 8, and we have two distinct clusters moving NW and SE).
  * "Scattering/Deflection": gliders survive but their paths/directions are altered, or they are deflected, with stable final bit counts.
  * "Chaos": final bit count explodes (e.g., > 12 bits or chaotic growth).
- Save the results of all 117 runs to a JSON file `archive/iter_239/results/scattering_sweep_results.json` and a CSV file `archive/iter_239/results/scattering_sweep_results.csv`.
- Ensure everything is fully tested, run the sweep, and verify that it completes successfully without any errors. Do not use promotional language in any logs or outputs. Use disciplined scientific terms: "consistent with", "evidence for", "does not refute", "refuted by".

Let's run!