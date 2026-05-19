This is a re-run of the diagnostic task 219.4. The goal is to check for a hang in the core simulation script, using the cleaned rule file.

1.  Use the cleaned rule file located at `archive/iter_219/results/g4_rule_083_cleaned.json`.
2.  Execute `src/run_simulation.py` with this rule file.
3.  **CRITICAL:** Set a very short number of steps: `--num_steps 20`.
4.  Set a hard timeout for the entire process to 60 seconds.
5.  The goal is to verify that a short simulation completes without hanging.
6.  If it completes successfully, report `status: ok` and a metric `completed_in_time: true`.
7.  If it hangs or times out, report `status: experiment_failed`, a metric `completed_in_time: false`, and summarize any logs from `stderr.txt` in the `experimenter_view`.