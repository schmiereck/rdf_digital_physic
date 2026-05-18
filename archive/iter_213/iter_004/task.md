**Objective: Restore the missing `src/automata_lib` directory to fix the platform instability.**

**Context:**
The diagnostic planner `213.3` has definitively proven that the platform is failing due to a `ModuleNotFoundError`. The required local dependency, the `src/automata_lib` directory, is missing.

**Your Task:**
You are to restore this critical dependency from a backup in a previous successful iteration.

1.  **Locate Source:** Examine the file listings of recent successful simulation iterations like `iter_195`, `iter_193`, or `iter_179`. Find one that contains the full `src/automata_lib` directory in its archive.
2.  **Restore Directory:** Copy the *entire* `src/automata_lib` directory and its contents from the `archive/iter_NNN/src/automata_lib` of the iteration you chose into the current, active `src/` directory.
3.  **Verify Fix:** Execute the diagnostic script `src/minimal_crash_example.py`, which was created in `213.3`. This script is designed to fail with a `ModuleNotFoundError` if the library is missing.

**Success Criterion:**
The task is successful if `src/minimal_crash_example.py` runs without raising a `ModuleNotFoundError`. The script is expected to print a success message and exit cleanly.
