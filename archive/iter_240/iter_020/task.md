1. Edit `src/rigorous_glider_audit.py` to implement the robust original-orientation simulation pipeline:
   - For each candidate (175 new + 1 reference), run the 200-step simulation on its ORIGINAL, unrotated particle.
   - A candidate is stable if bit count is perfectly conserved AND max extent <= 6 at every step.
   - For stable candidates only, group them into O_h orbits using `oh_canonical()`. (Two candidates belong to the same orbit if they have the same canonical form).
   - For each unique O_h orbit, choose one stable candidate as the representative to report the class's properties (period, speed, etc.).
   - Write the audited taxonomy JSON to `archive/iter_240/results/audited_glider_taxonomy.json` and the markdown report to `archive/iter_240/results/audited_glider_taxonomy_report.md`.
2. Run `python src/rigorous_glider_audit.py`.
3. Display the summary output from the terminal.
4. Verify that the reference glider LUT-08 is now correctly classified as STABLE (since we simulate its original unrotated configuration), and see how many unique STABLE glider orbits are found and if they are disjoint from LUT-08.