**Objective: Diagnose the silent crash in the `automata-lib` library.**

The sub-planner in `213.1` reported that every attempt to use `automata-lib` resulted in a silent crash with no error output, making it impossible to proceed with any simulations. Your task is to perform a deep diagnostic to isolate the root cause of this failure.

**Methodology: Incremental Probing**

You must create and execute a series of minimal Python scripts to pinpoint the exact function call that triggers the crash. Do not write one large script; create and run them one by one, from simplest to most complex.

1.  **Script 1 (Basic Import):** Write a script that only imports the necessary components from `automata_lib.ca`. Run it. If it crashes, the problem is in the library's initialization.
2.  **Script 2 (Grid Creation):** If Script 1 succeeds, write a new script that imports the library AND creates a simple `HexGrid` instance. Run it. This will test the grid object's constructor.
3.  **Script 3 (Rule Loading):** If Script 2 succeeds, add code to load a known-good rule file (e.g., the `g10_rule_001.json` found by `iter_179`). This will test the rule parsing and loading mechanism.
4.  **Script 4 (Seeding):** If Script 3 succeeds, add code to seed the grid with a simple pattern like the L-tromino.
5.  **Script 5 (Single Step):** If Script 4 succeeds, add the `grid.step()` call. This is the most likely point of failure.

**Your Goal:**
Your final output must be a minimal, reproducible example (`src/minimal_crash_example.py`) that reliably triggers the silent crash, along with a brief analysis of which specific component or function call is the culprit. This script will be the input for the next agent, which will be tasked with fixing the bug.
