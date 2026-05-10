#!/usr/bin/env python3
"""Characterize two-bit ('11') initial condition interactions under glider rules."""
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RULES_PATH = PROJECT_ROOT / "archive" / "iter_001" / "results" / "valid_rules.json"
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_018" / "results"
RESULT_YAML = RESULTS_DIR / "result.yaml"

LATTICE_SIZE = 100
NUM_STEPS = 100

# Glider rule indices from iter_002 (rules 5–26, 22 total)
GLIDER_RULE_INDICES = list(range(5, 27))


def step(state, rule):
    n = len(state)
    new_state = [0] * n
    for i in range(n):
        left = state[(i - 1) % n]
        center = state[i]
        right = state[(i + 1) % n]
        output = rule[f"{left}{center}{right}"]
        new_state[i] = int(output[1])
    return new_state


def simulate(rule):
    state = [0] * LATTICE_SIZE
    state[49] = 1
    state[50] = 1
    history = [tuple(state)]
    for _ in range(NUM_STEPS):
        state = step(state, rule)
        history.append(tuple(state))
    return history


def count_isolated_ones(state):
    n = len(state)
    return sum(
        1 for i in range(n)
        if state[i] == 1 and state[(i - 1) % n] == 0 and state[(i + 1) % n] == 0
    )


def count_adjacent_ones(state):
    """Count pairs of adjacent 1-bits."""
    n = len(state)
    return sum(1 for i in range(n) if state[i] == 1 and state[(i + 1) % n] == 1)


def classify(history):
    # ANNIHILATION: final state is all zeros
    if sum(history[-1]) == 0:
        return "ANNIHILATION"

    # ELASTIC: check for two isolated 1-bits in multiple windows.
    # With v=c gliders on a 100-cell lattice, wrap-around re-collision occurs near
    # step 50, so we inspect windows before and after that event.
    windows = [history[5:25], history[55:75]]
    for window in windows:
        isolated = [count_isolated_ones(s) for s in window]
        if all(c == 2 for c in isolated):
            return "ELASTIC"

    # FUSION (moving bound state): the '11' pair travels as a unit at v=c.
    # Detected when the two bits remain adjacent throughout a free-flight window.
    window_5_40 = history[5:40]
    adjacent = [count_adjacent_ones(s) for s in window_5_40]
    if all(c == 1 for c in adjacent):
        return "FUSION"

    # FUSION (stationary or slow): periodic pattern in the tail
    tail = history[-40:]
    for period in range(1, 21):
        if all(tail[-1 - k] == tail[-1 - k - period] for k in range(10)):
            return "FUSION"

    return "CHAOTIC"


def render_spacetime(history, width=100):
    lines = []
    for state in history:
        lines.append("".join("#" if v else "." for v in state))
    return "\n".join(lines)


def write_yaml(path, data):
    lines = []
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    with open(RULES_PATH, encoding="utf-8") as f:
        all_rules = json.load(f)
    print(f"Loaded {len(all_rules)} total rules; testing {len(GLIDER_RULE_INDICES)} glider rules")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    counts = {"ELASTIC": 0, "FUSION": 0, "ANNIHILATION": 0, "CHAOTIC": 0}
    by_outcome = {"ELASTIC": [], "FUSION": [], "ANNIHILATION": [], "CHAOTIC": []}

    for idx in GLIDER_RULE_INDICES:
        rule = all_rules[idx]
        history = simulate(rule)
        outcome = classify(history)
        counts[outcome] += 1
        by_outcome[outcome].append(idx)

        # Save spacetime diagram for non-chaotic outcomes
        if outcome != "CHAOTIC":
            diagram = render_spacetime(history)
            (RESULTS_DIR / f"spacetime_rule_{idx}_{outcome.lower()}.txt").write_text(
                diagram + "\n", encoding="utf-8"
            )

        print(f"Rule {idx:2d}: {outcome}  (final ones={sum(history[-1])})")

    total = sum(counts.values())
    print(f"\nRules tested : {total}")
    print(f"ELASTIC      : {counts['ELASTIC']}  {by_outcome['ELASTIC']}")
    print(f"FUSION       : {counts['FUSION']}  {by_outcome['FUSION']}")
    print(f"ANNIHILATION : {counts['ANNIHILATION']}  {by_outcome['ANNIHILATION']}")
    print(f"CHAOTIC      : {counts['CHAOTIC']}  {by_outcome['CHAOTIC']}")

    result = {
        "rules_tested": total,
        "elastic_collisions": counts["ELASTIC"],
        "fusions": counts["FUSION"],
        "annihilations": counts["ANNIHILATION"],
        "chaotic_outcomes": counts["CHAOTIC"],
        "elastic_rule_indices": by_outcome["ELASTIC"],
        "fusion_rule_indices": by_outcome["FUSION"],
        "annihilation_rule_indices": by_outcome["ANNIHILATION"],
        "chaotic_rule_indices": by_outcome["CHAOTIC"],
    }
    write_yaml(RESULT_YAML, result)
    print(f"\nWritten: {RESULT_YAML}")

    success = total == 22 and (counts["ELASTIC"] > 0 or counts["FUSION"] > 0)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
