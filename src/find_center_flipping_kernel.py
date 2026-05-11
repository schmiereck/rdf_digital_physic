"""
iter_038: Search for a state-pair (A, B) that is:
  1. Center-Bit Flip: center bit of A != center bit of B
  2. Disjoint Orbits: B is NOT in A's rotational orbit
  3. Conflict-Free Closure: joint 12-state rotational closure has exactly 12 unique states
"""
import itertools
import yaml
import os

RESULT_DIR = os.path.join(os.path.dirname(__file__), "..", "archive", "iter_038", "results")
RESULT_FILE = os.path.join(os.path.dirname(__file__), "..", "archive", "iter_038", "result.yaml")


def rotate_neighborhood(state: int, steps: int) -> int:
    """Rotate the 6 neighbor bits of a 7-bit state clockwise by `steps`.

    Bit layout: bit 0 = center (fixed under rotation), bits 1-6 = neighbors clockwise.
    """
    center = state & 1
    neighbors = (state >> 1) & 0x3F
    steps = steps % 6
    if steps == 0:
        return state
    rotated = ((neighbors << steps) | (neighbors >> (6 - steps))) & 0x3F
    return center | (rotated << 1)


def get_center_bit(state: int) -> int:
    """Return the center bit (bit 0) of a 7-bit state."""
    return state & 1


def get_orbit(state: int) -> frozenset:
    """Return the full rotational orbit of a state (up to 6 rotations)."""
    return frozenset(rotate_neighborhood(state, i) for i in range(6))


def search_weight(w: int):
    """Search all pairs of 7-bit states with Hamming weight w. Returns (pairs_checked, valid_pair or None)."""
    states = [s for s in range(128) if bin(s).count("1") == w]
    print(f"W={w} states found: {len(states)}")

    pairs_checked = 0

    for A, B in itertools.combinations(states, 2):
        pairs_checked += 1

        # Check 1 (cheapest): center bits must differ
        if get_center_bit(A) == get_center_bit(B):
            continue

        # Check 2: B must NOT be in A's rotational orbit (disjoint orbits)
        orbit_A = get_orbit(A)
        if B in orbit_A:
            continue

        # Check 3: joint rotational closure must have exactly 12 elements
        closure = set()
        for i in range(6):
            closure.add(rotate_neighborhood(A, i))
            closure.add(rotate_neighborhood(B, i))
        if len(closure) == 12:
            print(f"Valid kernel found at pair #{pairs_checked}!")
            return pairs_checked, (A, B)

    return pairs_checked, None


def main():
    total_pairs = 0
    valid_kernel = None
    found_weight = None

    for w in [2, 3]:
        pairs_checked, result = search_weight(w)
        total_pairs += pairs_checked
        if result is not None:
            valid_kernel = result
            found_weight = w
            break

    found = valid_kernel is not None
    yaml_result = {
        "valid_kernel_found": found,
        "hamming_weight_searched": found_weight if found_weight is not None else "none",
        "pairs_checked": total_pairs,
    }

    if found:
        A, B = valid_kernel
        orbit_A = get_orbit(A)
        orbit_B = get_orbit(B)
        closure = set()
        for i in range(6):
            closure.add(rotate_neighborhood(A, i))
            closure.add(rotate_neighborhood(B, i))

        yaml_result["kernel_A"] = int(A)
        yaml_result["kernel_B"] = int(B)
        yaml_result["kernel_A_binary"] = format(A, "07b")
        yaml_result["kernel_B_binary"] = format(B, "07b")

        print(f"  A = {A} ({format(A, '07b')}), center_bit={get_center_bit(A)}")
        print(f"  B = {B} ({format(B, '07b')}), center_bit={get_center_bit(B)}")
        print(f"  Center bits differ: {get_center_bit(A) != get_center_bit(B)}")
        print(f"  Orbit of A: {sorted(orbit_A)}")
        print(f"  Orbit of B: {sorted(orbit_B)}")
        print(f"  B in orbit(A): {B in orbit_A}")
        print(f"  Orbits disjoint: {orbit_A.isdisjoint(orbit_B)}")
        print(f"  Closure size: {len(closure)} (must be 12)")
    else:
        print("No valid kernel found.")

    os.makedirs(RESULT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(RESULT_FILE), exist_ok=True)

    with open(RESULT_FILE, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False)

    print(f"\nResults written to {RESULT_FILE}")
    return yaml_result


if __name__ == "__main__":
    main()
