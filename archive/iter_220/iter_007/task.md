1. Run 'python src/run_evolution_exp_220.py' to perform the evolutionary search for a sub-light speed (v<c) glider using the validated DisplacementConsistencyFitness function.
2. Confirm that the run completes successfully and writes outputs (champion_rule.json, evolution_summary.csv, and any other files) to 'archive/iter_220/results/'.
3. Analyze the champion rule: What is its fitness? What is its average velocity (is it indeed v<c, e.g. < 0.9c)? Does it conserve bits perfectly? Is it a true glider rather than an exploit (puffer, drifter, explosive bloomer)?
4. If a champion glider is found, make sure a GIF is rendered showing its motion and saved in 'archive/iter_220/results/'.
5. Provide a summary of the metrics and findings.