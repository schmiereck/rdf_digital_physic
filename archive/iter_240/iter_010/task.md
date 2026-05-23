Execute this exact command in the terminal to run the audit script:
`PYTHONPATH=. python src/rigorous_glider_audit.py`

This will rigorously audit all 163 gliders, verify their 200-step stability in vacuum, group them into O_h equivalence classes, normalize their velocities, and write the output files to `archive/iter_240/results/`. Ensure the execution completes successfully.