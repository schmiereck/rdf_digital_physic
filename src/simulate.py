#!/usr/bin/env python3
"""
Composite two-cell particle CA: produces a v=c/2 glider.

Particle representation (2-bit cells):
  0 = '00' (empty)
  1 = '01' (state A, leading half)
  2 = '10' (state B, trailing half)

Two-cell particle pattern: [1, 2] at positions (i, i+1).

Phase OSCILLATE (even t): [1,2] at (i,i+1) -> [2,1] in-place (flip internal state)
Phase MOVE (odd t):       [2,1] at (i,i+1) -> [1,2] at (i+1,i+2) (translate right)

Effective velocity = 1 cell per 2 steps = c/2.
"""
import sys
from pathlib import Path

LATTICE_SIZE = 100
INITIAL_POS = 20
STEPS = 100

RESULTS_DIR = Path(__file__).parent.parent / "archive" / "iter_014" / "results"
RESULT_YAML = RESULTS_DIR / "result.yaml"

# Rule tables: (L, C, R) -> new C; all other neighborhoods default to identity (output = C)

# OSCILLATE: flip [1,2] <-> [2,1] in place (neighbors must be empty)
OSCILLATE_RULE = {
    (0, 1, 2): 2,  # '01' with '10' right: flip to '10'
    (1, 2, 0): 1,  # '10' with '01' left: flip to '01'
}

# MOVE: shift [2,1] one step right, restoring to [1,2]
MOVE_RULE = {
    (0, 2, 1): 0,  # leading '10' with '01' right: vacate -> '00'
    (1, 0, 0): 2,  # empty cell with '01' left: plant '10'
    # (2, 1, 0) -> 1 is already identity; listed here for clarity
}


def apply_rule(lattice, rule_table):
    n = len(lattice)
    new = list(lattice)
    for i in range(n):
        L = lattice[(i - 1) % n]
        C = lattice[i]
        R = lattice[(i + 1) % n]
        new[i] = rule_table.get((L, C, R), C)
    return new


def center_of_mass(lattice):
    positions = [i for i, v in enumerate(lattice) if v > 0]
    return sum(positions) / len(positions) if positions else None


def is_particle_intact(lattice):
    active = [i for i, v in enumerate(lattice) if v > 0]
    if len(active) != 2:
        return False
    if active[1] - active[0] != 1:
        return False
    pattern = (lattice[active[0]], lattice[active[1]])
    return pattern in ((1, 2), (2, 1))


def write_yaml(path, data):
    lines = []
    for key, value in data.items():
        if isinstance(value, bool):
            lines.append(f"{key}: {str(value).lower()}")
        else:
            lines.append(f"{key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    lattice = [0] * LATTICE_SIZE
    lattice[INITIAL_POS] = 1      # '01' = state A (leading half)
    lattice[INITIAL_POS + 1] = 2  # '10' = state B (trailing half)

    history = [list(lattice)]
    positions = [center_of_mass(lattice)]

    for t in range(STEPS):
        if t % 2 == 0:
            lattice = apply_rule(lattice, OSCILLATE_RULE)
        else:
            lattice = apply_rule(lattice, MOVE_RULE)
        history.append(list(lattice))
        positions.append(center_of_mass(lattice))

    # Effective velocity over full run
    valid = [(i, p) for i, p in enumerate(positions) if p is not None]
    if len(valid) >= 2:
        t0, x0 = valid[0]
        tf, xf = valid[-1]
        velocity = (xf - x0) / (tf - t0) if tf > t0 else 0.0
    else:
        velocity = 0.0

    # Stability: particle must stay as a contiguous 2-cell pattern throughout
    is_stable = all(is_particle_intact(history[i]) for i in range(len(history)))

    final_pos = positions[-1] if positions[-1] is not None else positions[-2]

    if is_stable and 0.49 <= velocity <= 0.51:
        behavior_class = "COMPOSITE_GLIDER"
    elif not is_stable:
        behavior_class = "DECAY"
    elif abs(velocity) < 0.01:
        behavior_class = "STATIONARY_OSCILLATOR"
    else:
        behavior_class = "CHAOTIC"

    result = {
        "behavior_class": behavior_class,
        "effective_velocity": round(float(velocity), 6),
        "is_stable": bool(is_stable),
        "final_position": float(final_pos) if final_pos is not None else None,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    write_yaml(RESULT_YAML, result)

    print(f"behavior_class:     {behavior_class}")
    print(f"effective_velocity: {velocity:.6f}")
    print(f"is_stable:          {is_stable}")
    print(f"final_position:     {final_pos}")
    print()
    print("Position trace (every 10 steps):")
    for i in range(0, STEPS + 1, 10):
        if i < len(positions):
            print(f"  t={i:4d}  pos={positions[i]}")

    return 0 if behavior_class == "COMPOSITE_GLIDER" else 1


if __name__ == "__main__":
    sys.exit(main())
