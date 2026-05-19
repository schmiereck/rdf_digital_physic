The previous agent (219.3) hung and was stopped. This task is a diagnostic to determine if `src/run_simulation.py` has a bug that causes it to hang with the rule from iter_218.

1.  Load the champion rule `g4_rule_083` from `archive/iter_218/results/champion_rule.json`.
2.  Execute `src/run_simulation.py` using this rule.
3.  **CRITICAL:** Set a very short number of steps: `--num_steps 20`.
4.  Add verbose logging to the execution command if possible.
5.  Set a hard timeout for the process to 60 seconds to prevent another hang.
6.  The primary goal is to see if the run completes successfully.
7.  If it completes, report `status: ok` and a metric `completed_in_time: true`.
8.  If it hangs and times out, report `status: experiment_failed` and a metric `completed_in_time: false`.
9.  Examine `stdout.txt` and `stderr.txt` for any error messages or clues about a possible infinite loop. Summarize findings in the `experimenter_view`.