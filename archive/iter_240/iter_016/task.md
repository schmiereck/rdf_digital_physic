Write and run a script `src/find_mapping.py` to find the exact 3x3 projection matrix $B^T$ and the 1-to-1 mapping $P$ from Cartesian FCC vectors $C$ to projected shifts $S$, using the 3-vector linear independence solver.
The script must:
1. Load `SHIFTS` from `src.engine_3d` as $S$ (12x3).
2. Load `fcc_neighbor_vectors` from `src.search_3d_gliders` as $C$ (12x3).
3. Find distinct indices $i_0, i_1, i_2$ in $C$ such that $C[[i_0, i_1, i_2]]$ is invertible, and compute candidate $B^T = \text{inv}(C[[i_0, i_1, i_2]]) S[[0, 2, 6]]$.
4. Check if the candidate $B^T$ projects $C$ to $S$ bijectively (with distance < 1e-10 for each pair).
5. Print the working $P$ (where $P[i] = j$ means Cartesian channel $i$ maps to projected channel $j$) and the max error.
6. Verify that under this mapping, all 48 O_h permutations can be reconstructed on $S$ with error < 1e-12.
7. Print the python code for `build_oh_transforms()` that integrates this exact mapping.