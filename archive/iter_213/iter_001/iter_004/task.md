
We are now debugging the execution environment. All previous attempts at writing scripts have failed with a silent crash.

**Your task is to create and run a minimal diagnostic script.**

1.  **Create the script `src/diagnose.py`.**
2.  The script should contain the simplest possible code to run a simulation using `automata-lib`:
    *   Import `Automaton`, `Grid`, and `rules`.
    *   Use the `L_TROMINO` seed from `automata_lib.seeds`.
    *   Use the Game of Life rule: `rules.string_to_lambda("B3/S23")`.
    *   Create a `Grid` of size 50x50.
    *   Create an `Automaton` with the rule and seed.
    *   Run the automaton for only **10 steps**.
    *   After the `run` command finishes, print a clear success message like "DIAGNOSTIC SCRIPT COMPLETED SUCCESSFULLY."
3.  **Execute the script:** Run `python src/diagnose.py`.

The goal is to see if even this minimal script can run without crashing. If it succeeds, it will print the success message. If it fails silently like the others, it will confirm a deep problem with the library.

Please be very direct in your implementation. No complex features.
