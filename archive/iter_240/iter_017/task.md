1. Edit `src/rigorous_glider_audit.py` to replace `build_oh_transforms()` with the exact working implementation:
```python
def build_oh_transforms():
    S = np.array(SHIFTS, dtype=float)
    S_pinv = np.linalg.pinv(S)
    C = fcc_neighbor_vectors().astype(float)
    
    # Selected indices from 3-vector solver
    i0, i1, i2 = 0, 4, 8
    C_sub = C[[i0, i1, i2]]
    S_sub = S[[0, 2, 6]]
    
    BT = np.linalg.inv(C_sub) @ S_sub
    
    # Bijective mapping P (Cartesian -> Projected)
    P = [0, 10, 7, 1, 2, 11, 8, 3, 6, 4, 5, 9]
    
    perms_cart = get_oh_permutations()
    transforms = []
    max_err = 0.0
    for p_cart in perms_cart:
        p_proj = [0] * 12
        for i in range(12):
            p_proj[P[i]] = P[p_cart[i]]
        p_proj = tuple(p_proj)
        
        S_rot = np.array([S[p_proj[i]] for i in range(12)], dtype=float)
        M_g = S_rot.T @ S_pinv.T
        err = np.max(np.abs(S @ M_g.T - S_rot))
        max_err = max(max_err, err)
        transforms.append((p_proj, M_g))
        
    assert max_err < 1e-10, f"O_h transform reconstruction error too large: {max_err}"
    return transforms
```
2. Run `python3 src/rigorous_glider_audit.py`.
3. Display the full terminal output from this run.
4. Verify that it correctly groups the candidates (including reference glider) and find how many unique O_h equivalence classes are STABLE and if any are disjoint from the LUT-08 reference orbit!
5. Check if the generated taxonomy and reports exist.