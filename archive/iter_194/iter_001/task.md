The goal is to check the robustness of the elastic collision discovery from iter_193. The final population from that search is in `archive/iter_193/iter_002/results/final_population.json`, and the champion rule (rank 1) is already known to be elastic. 

Your task is to take the next 4 best rules from that population (ranks 2-5) and re-simulate their collision dynamics. For each of these four rules:
1. Load the rule from the final population file.
2. Run a 400-step simulation using the standard two-glider collision seed (from `src/seeds.py`, `create_colliding_gliders_seed`).
3. Generate a GIF animation of the simulation. Save it to `archive/iter_194/results/rank_N_collision.gif`, where N is the rule's rank (2, 3, 4, 5).
4. Write a summary file, `archive/iter_194/results/robustness_check.json`, containing an entry for each of the 4 tested rules, classifying the outcome as 'elastic', 'inelastic_fusion', 'inelastic_annihilation', or 'chaotic'.