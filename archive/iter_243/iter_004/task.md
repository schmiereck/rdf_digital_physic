Write a Python script `src/glider_annihilation_analysis.py` containing the self-contained analysis code and execute it.

The script must:
1. Load `archive/iter_224/results/glider_00_lut08_sub03.json`.
2. Compute original velocity of glider pA.
3. Identify antiparticles using O_h transformations from `src/rigorous_glider_audit.py` with velocity -v_A.
4. Perform collision sweep over antiparticles, phases, and offsets.
5. Verify "clean annihilation" (8 bits total, 0 bits in 10x10x10 box around (16,16,16), min pairwise distance >= 6).
6. Run the forward-backward CPT-reversibility test and verify perfect bit-level reconstruction.
7. Write `archive/iter_243/results/annihilation_summary.json` and `archive/iter_243/results/CPT_annihilation_report.md`.

Execute the script with `python src/glider_annihilation_analysis.py` and print the stdout/stderr.