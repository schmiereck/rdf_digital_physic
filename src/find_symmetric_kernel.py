"""
Combinatorial search for a reversible, bit-conserving state-pair (A, B)
whose 6-fold rotational closure is conflict-free (size == 12).

7-bit state layout: bit 0 = center cell, bits 1-6 = 6 neighbors (clockwise).
"""

import itertools
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def rotate_neighborhood(state: int, steps: int) -> int:
    """Rotate the 6 neighbor bits of a 7-bit state clockwise by `steps`."""
    center = state & 1
    neighbors = (state >> 1) & 0x3F
    steps = steps % 6
    if steps == 0:
        return state
    rotated = ((neighbors << steps) | (neighbors >> (6 - steps))) & 0x3F
    return center | (rotated << 1)


def hamming_weight(x: int) -> int:
    return bin(x).count('1')


def main():
    # All 7-bit states with Hamming weight 2
    w2_states = [s for s in range(128) if hamming_weight(s) == 2]
    assert len(w2_states) == 21, f"Expected 21 W=2 states, got {len(w2_states)}"

    print(f"Searching over {len(w2_states)} W=2 states ({len(w2_states)*(len(w2_states)-1)//2} pairs)...")

    pairs_checked = 0
    valid_pair = None

    for A, B in itertools.combinations(w2_states, 2):
        pairs_checked += 1

        closure = set()
        for i in range(6):
            closure.add(rotate_neighborhood(A, i))
            closure.add(rotate_neighborhood(B, i))

        if len(closure) == 12:
            valid_pair = (A, B)
            print(f"Conflict-free pair found at pair #{pairs_checked}!")
            break

    # Report
    found = valid_pair is not None
    kA = int(valid_pair[0]) if found else None
    kB = int(valid_pair[1]) if found else None
    kA_bin = format(kA, '07b') if found else None
    kB_bin = format(kB, '07b') if found else None

    print(f"\n--- Result ---")
    print(f"valid_kernel_found:   {found}")
    print(f"hamming_weight_searched: 2")
    print(f"pairs_checked:        {pairs_checked}")
    print(f"kernel_A:             {kA}  ({kA_bin})")
    print(f"kernel_B:             {kB}  ({kB_bin})")

    if found:
        print(f"\nRotational closure of A ({kA_bin}):")
        closure_A = sorted({rotate_neighborhood(kA, i) for i in range(6)})
        for s in closure_A:
            print(f"  {s:3d}  {s:07b}")
        print(f"Rotational closure of B ({kB_bin}):")
        closure_B = sorted({rotate_neighborhood(kB, i) for i in range(6)})
        for s in closure_B:
            print(f"  {s:3d}  {s:07b}")

    # Write result.yaml
    result_data = {
        'valid_kernel_found': found,
        'hamming_weight_searched': 2,
        'pairs_checked': pairs_checked,
        'kernel_A': kA,
        'kernel_B': kB,
        'kernel_A_binary': kA_bin,
        'kernel_B_binary': kB_bin,
    }

    out_dir = Path(__file__).parent.parent / "archive" / "iter_033"
    out_dir.mkdir(parents=True, exist_ok=True)
    results_dir = out_dir / "results"
    results_dir.mkdir(exist_ok=True)

    result_path = out_dir / "result.yaml"
    if HAS_YAML:
        with open(result_path, 'w') as f:
            yaml.dump(result_data, f, default_flow_style=False, sort_keys=False)
    else:
        with open(result_path, 'w') as f:
            for k, v in result_data.items():
                if v is None:
                    f.write(f"{k}: null\n")
                elif isinstance(v, bool):
                    f.write(f"{k}: {str(v).lower()}\n")
                elif isinstance(v, str):
                    f.write(f"{k}: '{v}'\n")
                else:
                    f.write(f"{k}: {v}\n")

    print(f"\nResult written to {result_path}")


if __name__ == '__main__':
    main()
