
Execute the evolutionary search script `src/run_evosg.py` with a new random seed to investigate if the previous run was stuck in a local optimum.

**Configuration:**
- Fitness Function: `RobustCumulativeDisplacementFitness`
- Population Size: 100
- Generations: 20
- Particle Seed: `L-tromino`
- **Random Seed for initial population:** 43 (This must be different from the seed used in iter_202)
- Output directory for results: `archive/iter_203.1/results/`

**Command:**
```bash
python src/run_evosg.py \
  --fitness RobustCumulativeDisplacementFitness \
  --pop_size 100 \
  --generations 20 \
  --particle_seed L-tromino \
  --seed 43 \
  --output_dir archive/iter_203.1/results/
```

**Final YAML format for the script's output:**
The script should conclude by printing a YAML block to standard output with the following structure:

```yaml
status: ok
artifacts:
  - "archive/iter_203.1/results/champion_rule.json"
  - "archive/iter_203.1/results/fitness_log.csv"
metrics:
  best_fitness: <best_fitness_value>
  max_displacement: <max_displacement_achieved>
log_excerpt: |
  ... (last 20 lines of log output)
experimenter_view: |
  A qualitative summary of the run. Did it converge to stationary patterns again? Was there any indication of glider-like behavior?
notes: "Re-run with seed 43."
```
