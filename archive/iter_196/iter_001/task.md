**Goal:** Refactor the core simulation and evolution framework in `src/` to support a configurable number of bits per cell, specifically preparing for 2-bit/cell experiments.

**Context:** The current codebase is hardcoded for 1-bit/cell states. To find v<c gliders (which require internal oscillations), we must move to a multi-bit representation. This task is a pure code refactoring and validation effort.

**Requirements:**
1.  Modify the relevant classes (`HexagonalGrid`, `Rule`, fitness functions in `src/engine.py`, `src/rule.py`, `src/fitness.py`, etc.) to handle NumPy grids with a shape of `(height, width, bits_per_cell)`.
2.  The `Rule` class should be adapted to handle lookup keys based on multi-bit neighborhoods. The neighborhood state will no longer be a simple integer bitmask but an array or tuple of bit values.
3.  Ensure bit conservation logic in fitness functions correctly sums the bits across the new cell dimension.
4.  The changes must be configurable, ideally via a single `BITS_PER_CELL` constant or parameter.

**Validation (CRITICAL):**
To ensure the refactoring did not break existing functionality, you must run a validation test:
1.  Set `BITS_PER_CELL` to 1.
2.  Load the champion elastic collision rule from `archive/iter_193/iter_002/results/champion_rule.json`.
3.  Run a short simulation of the head-on collision (offset=0) as in `iter_195`.
4.  Verify that the simulation still produces a perfect, bit-conserving elastic collision.
5.  Place a confirmation of this successful validation in your `result.yaml`. This confirms backward compatibility.

**Final Output:**
-   Modified `src/` files committed to the project.
-   A `result.yaml` confirming the successful refactoring and the positive result of the backward-compatibility validation test.