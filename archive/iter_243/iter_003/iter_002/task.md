Write the python script `src/glider_annihilation_analysis.py`. Below is the complete code for the script:

```python
import os
import sys
import json
import numpy as np
from itertools import permutations as iperms, product

SHIFTS = [
    (0, 1, 0),
    (0, -1, 0),
    (0, 0, 1),
    (0, 0, -1),
    (0, 1, -1),
    (0, -1, 1),
    (1, 1, 1),
    (1, 1, 0),
    (1, 0, 1),
    (-1, -1, -1),
    (-1, -1, 0),
    (-1, 0, -1),
]

def fcc_neighbor_vectors():
    vecs = []
    for i in range(3):
        for j in range(i + 1, 3):
            for si in (-1, 1):
                for sj in (-1, 1):
                    v = [0, 0, 0]
                    v[i] = si
                    v[j] = sj
                    vecs.append(tuple(v))
    return np.array(vecs, dtype=int)

def get_oh_permutations():
    vecs = fcc_neighbor_vectors()
    vec_to_idx = {tuple(v): i for i, v in enumerate(vecs)}
    perms = []
    for perm in iperms(range(3)):
        for signs in product((-1, 1), repeat=3):
            sigma = []
            ok = True
            for v in vecs:
                v_new = [0, 0, 0]
                for k in range(3):
                    v_new[perm[k]] = signs[k] * int(v[k])
                key = tuple(v_new)
                if key not in vec_to_idx:
                    ok = False
                    break
                sigma.append(vec_to_idx[key])
            if not ok:
                continue
            perms.append(tuple(sigma))
    return sorted(set(perms))

def rotate_particle_list(part, g, perms):
    perm = perms[g]
    S = np.array(SHIFTS, dtype=float)
    S_pinv = np.linalg.pinv(S)
    S_rot = np.zeros_like(S)
    for i in range(12):
        S_rot[i] = S[perm[i]]
    M_g = S_rot.T @ S_pinv.T
    rotated = []
    for (dl, dr, dc, ch) in part:
        pos = np.array([dl, dr, dc], dtype=float)
        pos_rot = np.round(M_g @ pos).astype(int)
        ch_rot = perm[ch]
        rotated.append([int(pos_rot[0]), int(pos_rot[1]), int(pos_rot[2]), int(ch_rot)])
    return rotated

def compute_single_centroid(cells, L=32):
    cells = np.array(cells, dtype=float)[:, :3]
    anchor = cells[0]
    unwrapped = np.zeros_like(cells)
    for d in range(3):
        unwrapped[:, d] = anchor[d] + np.mod(cells[:, d] - anchor[d] + L/2, L) - L/2
    return np.mean(unwrapped, axis=0)

def simulate_sparse(initial_bits, lut, steps=80, L=32):
    current_bits = list(initial_bits)
    for step in range(steps):
        coords_dict = {}
        for x, y, z, ch in current_bits:
            key = (x, y, z)
            if key not in coords_dict:
                coords_dict[key] = []
            coords_dict[key].append(ch)
        collided_bits = []
        for (x, y, z), channels in coords_dict.items():
            state = 0
            for ch in channels:
                state |= (1 << ch)
            new_state = lut[state]
            for ch in range(12):
                if (new_state >> ch) & 1:
                    collided_bits.append((x, y, z, ch))
        current_bits = []
        for x, y, z, ch in collided_bits:
            dl, dr, dc = SHIFTS[ch]
            nx = (x + dl) % L
            ny = (y + dr) % L
            nz = (z + dc) % L
            current_bits.append((nx, ny, nz, ch))
    return current_bits

def compute_glider_velocity(particle, lut, steps=80, L=32):
    current_bits = [((16 + dl) % L, (16 + dr) % L, (16 + dc) % L, ch) for (dl, dr, dc, ch) in particle]
    c_0 = compute_single_centroid(current_bits, L)
    c_prev = c_0.copy()
    c_continuous = c_0.copy()
    for step in range(steps):
        current_bits = simulate_sparse(current_bits, lut, steps=1, L=L)
        if len(current_bits) != 4:
            return None, False
        c_t = compute_single_centroid(current_bits, L)
        step_change = np.mod(c_t - c_prev + L/2, L) - L/2
        c_continuous += step_change
        c_prev = c_t.copy()
    velocity = c_continuous - c_0
    return velocity, True

def apply_cpt_sparse(bits, L=32):
    return [((-x) % L, (-y) % L, (-z) % L, ch) for (x, y, z, ch) in bits]

def main():
    print("Loading glider and LUT data...")
    glider_path = "archive/iter_224/results/glider_00_lut08_sub03.json"
    with open(glider_path, "r") as f:
        data = json.load(f)
    pA = data["particle"]
    lut = np.array(data["lut"], dtype=np.uint16)
    L = 32
    
    print("Computing velocity of original glider pA...")
    v_A, ok = compute_glider_velocity(pA, lut, steps=80, L=L)
    if not ok:
        print("Failed to compute pA velocity.")
        sys.exit(1)
    print(f"v_A over 80 steps: {v_A}")
    
    print("Generating O_h point group symmetries...")
    perms = get_oh_permutations()
    print(f"Generated {len(perms)} permutations.")
    
    print("Identifying stable antiparticle candidates...")
    candidates = []
    for g in range(48):
        pB = rotate_particle_list(pA, g, perms)
        v_B, stable = compute_glider_velocity(pB, lut, steps=80, L=L)
        if stable and np.linalg.norm(v_B + v_A) < 1e-4:
            candidates.append((g, pB, v_B))
            print(f"g={g:2d}: stable antiparticle, velocity={v_B}")
            
    print(f"Found {len(candidates)} stable antiparticle candidates.")
    
    print("Starting parameter sweep...")
    working_configs = []
    scanned_count = 0
    
    for g, pB, v_B in candidates:
        for phase in [0, 1]:
            # Cache the original glider's bits for this phase
            if phase == 0:
                pA_bits = [((6 + dl) % L, (16 + dr) % L, (6 + dc) % L, ch) for (dl, dr, dc, ch) in pA]
            else:
                pA_bits = [((6 + dl) % L, (16 + dr) % L, (6 + dc) % L, ch) for (dl, dr, dc, ch) in pA]
                pA_bits = simulate_sparse(pA_bits, lut, steps=1, L=L)
            
            for dl, dr, dc in product(range(-4, 5), repeat=3):
                scanned_count += 1
                pB_bits = [((26 + dl + dl_b) % L, (16 + dr + dr_b) % L, (26 + dc + dc_b) % L, ch) for (dl_b, dr_b, dc_b, ch) in pB]
                initial_bits = pA_bits + pB_bits
                
                # Simulate 80 steps
                final_bits = simulate_sparse(initial_bits, lut, steps=80, L=L)
                if len(final_bits) != 8:
                    continue
                
                # Check empty bounding box
                box_empty = True
                for x, y, z, ch in final_bits:
                    if 11 <= x <= 20 and 11 <= y <= 20 and 11 <= z <= 20:
                        box_empty = False
                        break
                if not box_empty:
                    continue
                
                # Check isolation (pairwise Manhattan distance >= 6)
                isolated = True
                min_dist = 999
                for i in range(8):
                    for j in range(i + 1, 8):
                        p1 = final_bits[i][:3]
                        p2 = final_bits[j][:3]
                        dist = 0
                        for d in range(3):
                            diff = abs(p1[d] - p2[d])
                            dist += min(diff, L - diff)
                        if dist < min_dist:
                            min_dist = dist
                        if dist < 6:
                            isolated = False
                            break
                    if not isolated:
                        break
                if not isolated:
                    continue
                
                # Perform CPT-symmetry reconstruction test
                cpt_bits = apply_cpt_sparse(final_bits, L)
                reconstructed_bits = simulate_sparse(cpt_bits, lut, steps=80, L=L)
                final_reconstructed = apply_cpt_sparse(reconstructed_bits, L)
                
                reconstruction_success = set(final_reconstructed) == set(initial_bits)
                if reconstruction_success:
                    working_configs.append({
                        "antiparticle_g": g,
                        "phase": phase,
                        "dl": dl,
                        "dr": dr,
                        "dc": dc,
                        "min_pairwise_distance": min_dist,
                        "cpt_reconstruction_success": True
                    })
                    print(f"Annihilation found! g={g}, phase={phase}, offset=({dl},{dr},{dc}), min_dist={min_dist}")
                    
    print(f"Sweep complete. Scanned {scanned_count} setups, found {len(working_configs)} working configurations.")
    
    # Select cleanest
    best_config = None
    if working_configs:
        best_config = max(working_configs, key=lambda c: (c["min_pairwise_distance"], -(c["dl"]**2 + c["dr"]**2 + c["dc"]**2)))
        print(f"Best Configuration: {best_config}")
        
    # Write summary files
    os.makedirs("archive/iter_243/results", exist_ok=True)
    summary_path = "archive/iter_243/results/annihilation_summary.json"
    with open(summary_path, "w") as f:
        json.dump({
            "success": len(working_configs) > 0,
            "v_A": v_A.tolist(),
            "scanned_count": scanned_count,
            "antiparticles_g": [c[0] for c in candidates],
            "num_working_configs": len(working_configs),
            "best_config": best_config,
            "all_working_configs": working_configs
        }, f, indent=2)
    print(f"Written summary to: {summary_path}")
    
    # Write CPT_annihilation_report.md
    report_path = "archive/iter_243/results/CPT_annihilation_report.md"
    with open(report_path, "w") as f:
        f.write("# CPT-Symmetry and Glider Annihilation Report\\n\\n")
        f.write("## Overview\\n")
        f.write("This report presents the results of the 3D Face-Centered Cubic (FCC) Lattice Gas Cellular Automaton (LGCA) glider annihilation study.\\n\\n")
        f.write(f"The original glider $pA$ has displacement vector $v_A = {v_A.tolist()}$ over 80 steps.\\n\\n")
        f.write("## Stable Antiparticles\\n")
        f.write("Using the 48 octahedral $O_h$ symmetry transformations, we identified the following stable antiparticles propagating with velocity exactly $-v_A$:\\n\\n")
        f.write("| POINT GROUP g | STABLE | VELOCITY vector (over 80 steps) |\\n")
        f.write("| --- | --- | --- |\\n")
        for g, _, v_B in candidates:
            f.write(f"| {g} | Yes | {v_B.tolist()} |\\n")
        f.write("\\n")
        f.write("## Sweeps and Clean Annihilation\\n")
        f.write(f"We scanned {scanned_count} relative alignments and phases. We found {len(working_configs)} configurations that cleanly annihilate into 8 isolated 1-bit radiation states.\\n\\n")
        if best_config:
            f.write("### Best Annihilation Configuration\\n")
            f.write(f"- **Antiparticle point group g:** {best_config['antiparticle_g']}\\n")
            f.write(f"- **Relative phase:** {best_config['phase']}\\n")
            f.write(f"- **Alignment offset (dl, dr, dc):** ({best_config['dl']}, {best_config['dr']}, {best_config['dc']})\\n")
            f.write(f"- **Min pairwise Manhattan distance at step 80:** {best_config['min_pairwise_distance']}\\n")
            f.write(f"- **CPT-symmetry reconstruction success:** {best_config['cpt_reconstruction_success']}\\n\\n")
            f.write("## CPT Reconstruction Verification\\n")
            f.write("The chosen cleanest configuration perfectly passed the CPT-symmetry reconstruction test. ")
            f.write("By inverting coordinates of the step 80 state, simulating 80 steps forward under the forward rule, and inverting coordinates again, ")
            f.write("we reconstructed the initial step 0 grid to perfect, bit-level precision. This provides a rigorous algebraic verification ")
            f.write("of the time-reversibility of the underlying rule.\\n")
        else:
            f.write("### No clean annihilation configurations found.\\n")
    print(f"Written report to: {report_path}")

if __name__ == '__main__':
    main()
```

Save this code to `src/glider_annihilation_analysis.py`, run it, and capture its output. Verify that the files are written.