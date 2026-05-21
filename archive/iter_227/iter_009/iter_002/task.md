Please complete the following tasks using Python scripts to execute and handle file writing to ensure complete cross-platform compatibility on Windows (avoid using command-line pipelines like tee or Unix-specific commands):

1. Run the script `src/d4_lensing.py` using Python (you can run it via Python's subprocess or by importing and calling the script, or running python in a subprocess).
2. Capture the full stdout/stderr of the execution and write it to `src/lensing_test_output.txt`.
3. Append the captured output to the end of `src/d4_lensing.py` formatted as a clean, comment block (e.g., using python multi-line comments: `"""\n<output>\n"""` or single-line comments) so that `src/d4_lensing.py` remains perfectly valid Python code.
4. Verify that `src/lensing_test_output.txt` is non-empty and has the expected simulation results (e.g. Shapiro Delay, Deflection Angles, etc.).
5. Provide a summary of the captured output and confirm that all steps are complete.