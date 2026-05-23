In `src/rigorous_glider_audit.py`, please modify `build_oh_transforms` and `oh_canonical` to keep the 3x3 coordinate transformation matrix `M_g` as a float matrix instead of rounding it to an integer matrix (since in the non-orthogonal coordinate system, the rotation matrices are float matrices, but they map integer coordinate vectors to integer coordinate vectors).

Please replace `build_oh_transforms()` with:
```python
def build_oh_transforms():
    S = np.array(SHIFTS, dtype=float)
    S_pinv = np.linalg.pinv(S)
    perms = get_oh_permutations()
    transforms = []
    max_err = 0.0
    for perm in perms:
        S_rot = np.array([S[perm[i]] for i in range(12)], dtype=float)
        M_g = S_rot.T @ S_pinv.T
        # Sanity check using floats
        pred = S @ M_g.T
        err = float(np.max(np.abs(pred - S_rot)))
        max_err = max(max_err, err)
        transforms.append((perm, M_g))
    assert max_err < 1e-8, f"O_h transform reconstruction error too large: {max_err}"
    return transforms
```

And replace `oh_canonical()` with:
```python
def oh_canonical(particle, transforms):
    best = None
    for perm, M_g in transforms:
        transformed = []
        for (l, r, c, ch) in particle:
            v = M_g @ np.array([l, r, c], dtype=float)
            nl = int(np.round(v[0]))
            nr = int(np.round(v[1]))
            nc = int(np.round(v[2]))
            transformed.append((nl, nr, nc, int(perm[ch])))
        canon = particle_translation_canon(transformed)
        if best is None or canon < best:
            best = canon
    return best
```

After modifying these, execute the script:
`PYTHONPATH=. python src/rigorous_glider_audit.py`

Verify that it completes with no assertion errors, runs 200 simulation steps in vacuum for each equivalence class, and writes the output files `archive/iter_240/results/audited_glider_taxonomy.json` and `archive/iter_240/results/audited_glider_taxonomy_report.md`. Ensure that the terminal output is fully captured.