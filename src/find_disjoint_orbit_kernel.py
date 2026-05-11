"""
iter_036: Search for a reversible, bit-conserving state-pair (A, B) with W=2
where:
  1. B is NOT in A's rotational orbit (disjoint orbit check)
  2. The rotational closure {rotate(A,i), rotate(B,i) | i=0..5} has exactly 12 elements
"""
import itertools
import yaml
import os

RESULT_DIR = os.path.join(os.path.dirname(__file__), "..", "archive", "iter_036", "results")
RESULT_FILE = os.path.join(os.path.dirname(__file__), "..", "archive", "iter_036", "result.yaml")


def rotate_neighborhood(state: int, steps: int) -> int:
    """Rotate the 6 neighbor bits of a 7-bit state clockwise by `steps`.

    Bit layout: bit 0 = center (fixed), bits 1-6 = 6 neighbors clockwise.
    """
    center = state & 1
    neighbors = (state >> 1) & 0x3F
    steps = steps % 6
    if steps == 0:
        return state
    rotated = ((neighbors << steps) | (neighbors >> (6 - steps))) & 0x3F
    return center | (rotated << 1)


def get_orbit(state: int) -> set:
    """Return the full rotational orbit of a state (6 rotations)."""
    return {rotate_neighborhood(state, i) for i in range(6)}


def main():
    # All 7-bit states with Hamming weight 2
    w2_states = [s for s in range(128) if bin(s).count("1") == 2]
    print(f"W=2 states found: {len(w2_states)}")

    pairs_checked = 0
    valid_kernel = None

    for A, B in itertools.combinations(w2_states, 2):
        pairs_checked += 1

        # Check 1: disjoint orbit — B must NOT be in A's rotational orbit
        orbit_A = get_orbit(A)
        if B in orbit_A:
            continue

        # Check 2: conflict check — rotational closure must have exactly 12 elements
        closure = set()
        for i in range(6):
            closure.add(rotate_neighborhood(A, i))
            closure.add(rotate_neighborhood(B, i))
        if len(closure) == 12:
            valid_kernel = (A, B)
            print(f"Valid kernel found at pair #{pairs_checked}!")
            break

    found = valid_kernel is not None
    result = {
        "valid_kernel_found": found,
        "hamming_weight_searched": 2,
        "pairs_checked": pairs_checked,
    }

    if found:
        A, B = valid_kernel
        result["kernel_A"] = int(A)
        result["kernel_B"] = int(B)
        result["kernel_A_binary"] = format(A, "07b")
        result["kernel_B_binary"] = format(B, "07b")

        orbit_A = get_orbit(A)
        orbit_B = get_orbit(B)
        closure = set()
        for i in range(6):
            closure.add(rotate_neighborhood(A, i))
            closure.add(rotate_neighborhood(B, i))

        print(f"  A = {A} ({format(A, '07b')})")
        print(f"  B = {B} ({format(B, '07b')})")
        print(f"  Orbit of A: {sorted(orbit_A)}")
        print(f"  Orbit of B: {sorted(orbit_B)}")
        print(f"  B in orbit(A): {B in orbit_A}")
        print(f"  Closure size: {len(closure)} (must be 12)")
        print(f"  Orbits disjoint: {orbit_A.isdisjoint(orbit_B)}")
    else:
        print("No valid kernel found.")

    os.makedirs(RESULT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(RESULT_FILE), exist_ok=True)

    with open(RESULT_FILE, "w") as f:
        yaml.dump(result, f, default_flow_style=False)

    print(f"\nResults written to {RESULT_FILE}")
    return result


if __name__ == "__main__":
    main()
