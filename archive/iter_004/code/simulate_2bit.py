#!/usr/bin/env python3
"""1D cellular automaton simulator for 2-bit/cell lattice (iter_003 rule)."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_004" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_004" / "result.yaml"

LATTICE_SIZE = 100
NUM_STEPS = 50

RULE = {
    ('00', '01', '00'): '10',
    ('00', '10', '00'): '01',
}


def apply_rule(left, center, right):
    return RULE.get((left, center, right), center)


def step(state):
    n = len(state)
    return [
        apply_rule(state[(i - 1) % n], state[i], state[(i + 1) % n])
        for i in range(n)
    ]


def lattice_to_str(state):
    return ' '.join(state)


def detect_period(history, center_idx):
    central = [s[center_idx] for s in history]
    last = central[-1]
    for period in range(1, len(central)):
        if central[-1 - period] == last:
            # Verify the period holds for several cycles
            check_len = min(period * 4, len(central) - 1)
            if all(central[-1 - k] == central[-1 - k - period] for k in range(check_len)):
                return period
    return None


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    state = ['00'] * LATTICE_SIZE
    state[50] = '01'

    history = [list(state)]

    for step_num in range(NUM_STEPS):
        state = step(state)
        history.append(list(state))

    # Save steps 0-3 for inspection
    for i in range(min(4, len(history))):
        (RESULTS_DIR / f"step_{i:03d}.txt").write_text(lattice_to_str(history[i]) + "\n", encoding="utf-8")

    # Track central cell
    center_idx = 50
    central_history = [s[center_idx] for s in history]
    print("Central cell states (steps 0-10):", central_history[:11])

    # Classify behavior
    period = detect_period(history, center_idx)

    # Check if any non-zero cell ever spreads beyond center
    max_spread = max(
        max((abs(i - 50) for i, v in enumerate(s) if v != '00'), default=0)
        for s in history
    )

    if period is not None and max_spread == 0:
        behavior_class = "STATIONARY_OSCILLATION"
        oscillation_period = period
    elif period is not None:
        behavior_class = "STATIONARY_OSCILLATION"
        oscillation_period = period
    else:
        final = history[-1]
        if all(c == '00' for c in final):
            behavior_class = "DECAY"
            oscillation_period = 0
        elif final == history[-2]:
            behavior_class = "STABLE"
            oscillation_period = 1
        else:
            behavior_class = "CHAOTIC"
            oscillation_period = -1

    print(f"behavior_class: {behavior_class}")
    print(f"oscillation_period: {oscillation_period}")
    print(f"max_spread: {max_spread}")

    RESULT_YAML.write_text(
        f"behavior_class: {behavior_class}\noscillation_period: {oscillation_period}\n",
        encoding="utf-8",
    )
    print(f"Written: {RESULT_YAML}")

    return 0 if behavior_class == "STATIONARY_OSCILLATION" and oscillation_period == 2 else 1


if __name__ == "__main__":
    sys.exit(main())
