You are an elite scientific data-analysis and plotting agent. Your task is to write a Python script `src/plot_scattering_results.py` to analyze and visualize the results of our sub-light glider collision sweep.

Please perform the following actions:

1. READ SWEEP RESULTS:
- Load the JSON sweep results from `archive/iter_239/results/scattering_sweep_results.json`.

2. ANALYZE PERIODIC STRUCTURE:
- Programmatically confirm the periodic structure of the outcomes. Specifically, for each \Delta y, extract the list of outcomes across \Delta t \in [0, 12].
- Analyze if there is a periodic pattern with a period of 6 steps (since the glider has an internal state cycle of 6). Save this detailed analysis to a JSON file: `archive/iter_239/results/scattering_results_analysis.json`.
- State clearly in the JSON analysis that the results show "evidence for" the phase-dependent periodic nature of soliton-like collisions on the hex lattice, and that the hypothesis "does not refute" the existence of structured, deterministic, discrete phase-dependent scattering.

3. GENERATE THE 2D OUTCOME PHASE DIAGRAM:
- Use matplotlib to generate a publication-quality 2D heatmap/grid.
- The x-axis should be the Relative Temporal Phase Delay \Delta t (from 0 to 12).
- The y-axis should be the Transverse Spatial Offset \Delta y (from -4 to 4, ordered from +4 down to -4 so that the visual layout corresponds to spatial coordinates).
- Assign distinct, high-contrast colors to the four discrete categories:
  * Annihilation -> black (representing complete destruction)
  * Transmission -> lightblue or gray
  * Scattering/Deflection -> green
  * Chaos -> red or orange (representing explosive instability)
- Add a clear legend mapping these colors to the four categories.
- Label the axes clearly: "Relative Temporal Phase Delay \Delta t (steps)" and "Transverse Spatial Offset \Delta y (lattice units)".
- Title the plot: "Phase Diagram of v=0.469c Sub-light Glider Collisions\nRule A (champion_rule_perfect.json)".
- Save the resulting figure as `archive/iter_239/results/scattering_phase_diagram.png`.

4. VERIFY EVERYTHING:
- Run `src/plot_scattering_results.py` to make sure it generates both the plot and the JSON analysis successfully.
- Check that there are no errors and that the files are properly written.
- Ensure the language in your summary is objective, rigorous, and avoids promotional words. Use required scientific vocabulary: "consistent with", "evidence for", "does not refute", "refuted by".

Let's execute!