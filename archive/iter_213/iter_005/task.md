**Objective: Restore the missing `src/automata_lib` directory to fix the platform instability.**

**Context:**
This is the second attempt to restore this critical dependency. The previous attempt (`213.4`) failed because the assigned `medium` complexity agent could not execute. You, a `planner` agent, are being used for this simple task because the standard executor agents are unreliable.

**Your Task:**
You are to orchestrate the restoration of the `src/automata_lib` directory from a backup in a previous successful iteration.

1.  **Sub-task 1 (Locate & Restore):** Launch a sub-agent to perform the restoration.
    *   The sub-agent must first find a recent successful iteration (e.g., `195`, `193`, `179`) that contains the `src/automata_lib` directory in its archive.
    *   It must then copy the *entire* `src/automata_lib` directory and its contents into the current, active `src/` directory.
2.  **Sub-task 2 (Verify Fix):** If the first sub-task succeeds, launch a second sub-agent to execute the diagnostic script `src/minimal_crash_example.py`.

**Success Criterion:**
The overall task is successful if your second sub-agent runs `src/minimal_crash_example.py` and it executes without raising a `ModuleNotFoundError`. Your final report should confirm that the library has been restored and the platform is ready for the next phase.
