"""
iter_041: Search for the second state-pair (A, B) satisfying:
  1. Center-Bit Flip: center bit of A != center bit of B
  2. Disjoint Orbits: B is NOT in A's rotational orbit
  3. Conflict-Free Closure: joint 12-state rotational closure has exactly 12 unique states
"""
import itertools
import yaml
import os

RESULT_DIR = os.path.join(os.path.dirname(__file__), "..", "archive", "iter_041", "results")
RESULT_FILE = os.path.join(os.path.dirname(__file__), "..", "archive", "iter_041", "result.yaml")


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


def search_all_valid(w: int, max_find: int = 2):
    """Search all pairs of 7-bit states with Hamming weight w.
    Returns list of up to max_find valid (A, B) pairs and total pairs checked."""
    states = [s for s in range(128) if bin(s).count("1") == w]
    print(f"W={w} states found: {len(states)}")

    pairs_checked = 0
    found = []

    for A, B in itertools.combinations(states, 2):
        pairs_checked += 1

        if get_center_bit(A) == get_center_bit(B):
            continue

        orbit_A = get_orbit(A)
        if B in orbit_A:
            continue

        closure = set()
        for i in range(6):
            closure.add(rotate_neighborhood(A, i))
            closure.add(rotate_neighborhood(B, i))
        if len(closure) == 12:
            found.append((A, B))
            print(f"  Valid kernel #{len(found)} at pair #{pairs_checked}: A={A} ({A:07b}), B={B} ({B:07b})")
            if len(found) >= max_find:
                break

    return pairs_checked, found


def main():
    total_pairs = 0
    all_kernels = []
    found_weight = None

    for w in [2, 3]:
        pairs_checked, kernels = search_all_valid(w, max_find=2)
        total_pairs += pairs_checked
        all_kernels.extend(kernels)
        if len(all_kernels) >= 2:
            found_weight = w
            break

    second_kernel = all_kernels[1] if len(all_kernels) >= 2 else None
    found = second_kernel is not None

    yaml_result = {
        "valid_kernels_found": len(all_kernels),
        "hamming_weight_searched": found_weight if found_weight is not None else "none",
        "pairs_checked": total_pairs,
        "first_kernel": {"A": int(all_kernels[0][0]), "B": int(all_kernels[0][1])} if all_kernels else None,
    }

    if found:
        A, B = second_kernel
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

        print(f"\nSecond valid kernel:")
        print(f"  A = {A} ({format(A, '07b')}), center_bit={get_center_bit(A)}")
        print(f"  B = {B} ({format(B, '07b')}), center_bit={get_center_bit(B)}")
        print(f"  Center bits differ: {get_center_bit(A) != get_center_bit(B)}")
        print(f"  Orbit of A: {sorted(orbit_A)}")
        print(f"  Orbit of B: {sorted(orbit_B)}")
        print(f"  B in orbit(A): {B in orbit_A}")
        print(f"  Orbits disjoint: {orbit_A.isdisjoint(orbit_B)}")
        print(f"  Closure size: {len(closure)} (must be 12)")
    else:
        print("Second valid kernel not found.")

    os.makedirs(RESULT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(RESULT_FILE), exist_ok=True)

    with open(RESULT_FILE, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False)

    print(f"\nResults written to {RESULT_FILE}")
    return yaml_result


if __name__ == "__main__":
    main()
