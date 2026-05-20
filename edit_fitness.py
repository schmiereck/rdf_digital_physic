#!/usr/bin/env python3
"""
edit_fitness.py

Reads 'src/new_fitness.py', finds the line:
    sorted_history = sorted(sim_history, key=lambda e: e["step"])
inside class DisplacementConsistencyFitness, and inserts
center-of-mass unwrapping code right after it.

The unwrapping code fixes COM discontinuities that occur when
centre-of-mass coordinates wrap around toroidal grid boundaries.
Without unwrapping, small jumps from one edge to the other would
appear as large displacements.
"""

from pathlib import Path

FILE_PATH = Path("src/new_fitness.py")

UNWRAP_CODE = """
        # ------------------------------------------------------------------
        # Center-of-mass unwrapping to handle toroidal grid boundaries.
        # When the COM jumps from near one edge to the opposite edge,
        # raw displacement would be wrong.  We unwrap consecutive COM
        # deltas to remove artificial discontinuities.
        # ------------------------------------------------------------------
        unwrapped_coms: list[tuple[float, float]] = [sorted_history[0]["com"]]
        for i in range(1, len(sorted_history)):
            prev_com = unwrapped_coms[-1]
            cur_com = sorted_history[i]["com"]
            dx = cur_com[0] - prev_com[0]
            dy = cur_com[1] - prev_com[1]
            # Assume grid wraps at 128 (GRID_SIZE).  Unwrap deltas:
            if dx > 64:
                dx -= 128.0
            elif dx < -64:
                dx += 128.0
            if dy > 64:
                dy -= 128.0
            elif dy < -64:
                dy += 128.0
            unwrapped_coms.append((prev_com[0] + dx, prev_com[1] + dy))

        # Replace the raw COMs with unwrapped ones for downstream calc.
        unwrapped_history: list[dict] = []
        for i, entry in enumerate(sorted_history):
            unwrapped_entry = dict(entry)
            unwrapped_entry["com"] = unwrapped_coms[i]
            unwrapped_history.append(unwrapped_entry)
        sorted_history = unwrapped_history
"""


def main() -> None:
    content = FILE_PATH.read_text(encoding="utf-8")

    # The line to find — this specific instance is inside __call__ of
    # DisplacementConsistencyFitness.
    target_line = 'sorted_history = sorted(sim_history, key=lambda e: e["step"])'

    if target_line not in content:
        print(f"ERROR: target line not found in {FILE_PATH}")
        return

    # Insert the unwrapping code right after the target line.
    new_content = content.replace(target_line, target_line + UNWRAP_CODE, 1)

    FILE_PATH.write_text(new_content, encoding="utf-8")
    print(f"SUCCESS: Wrote unwrapping code into {FILE_PATH}")


if __name__ == "__main__":
    main()
