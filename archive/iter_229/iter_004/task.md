Fix the syntax error and LaTeX escaping issues in `src/run_latching_lensing_sweep.py`.

Specifically:
1. Locate the `f.write(...)` block starting around line 117.
2. Remove the `f` prefix from all the string parts inside that block (lines 118 to 125) and make them raw strings `r"..."` to prevent LaTeX backslashes from being evaluated as escape sequences or f-string variable substitutions.
3. Check other `f.write(...)` blocks containing backslashes (like `\mathcal` or `\Theta`) and make sure they are properly formatted as raw strings `r"..."` without an `f` prefix unless they contain actual formatting variables (and if they do, use double curly braces `{{` and `}}` for LaTeX curly braces).
4. Run the fixed script using `python src/run_latching_lensing_sweep.py`.
5. Verify that the script completes with output showing successful JSON and Markdown report generation.
6. Check that the files are written to `archive/iter_229/results/latching_lensing_sweep.json` and `archive/iter_229/results/latching_lensing_report.md`.