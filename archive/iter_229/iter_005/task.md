Fix the syntax errors in `src/run_latching_lensing_sweep.py` by converting the LaTeX string blocks into plain raw strings `r"..."`.

To do this robustly, create and execute a python script `src/fix_syntax.py` that:
1. Reads `src/run_latching_lensing_sweep.py`.
2. Locates any `f.write(...)` blocks that write LaTeX content (specifically searching for strings containing `\text`, `\mathcal`, `\Theta`, `\tau`, or curly braces `{}`).
3. Converts those strings to raw strings `r"..."` or raw triple-quoted strings `r"""..."""` and removes any `f` prefix.
4. Saves the corrected code back to `src/run_latching_lensing_sweep.py`.

Once the syntax is fixed, run `python src/run_latching_lensing_sweep.py` using the shell to execute the entire parameter sweep.
Verify that:
1. The script completes with no errors and exits with 0.
2. The results JSON file is successfully created at `archive/iter_229/results/latching_lensing_sweep.json`.
3. The Markdown report is successfully created at `archive/iter_229/results/latching_lensing_report.md`.

Confirm that all tests pass, and print out the complete execution logs.