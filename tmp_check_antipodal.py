import sys
sys.path.insert(0, 'src')
from search_3d_gliders import get_oh_permutations, precompute_perm_action
import numpy as np

perms = get_oh_permutations()
action = precompute_perm_action(perms)

# Antipodal transposition
antipodal = [1, 0, 3, 2, 5, 4, 9, 10, 11, 6, 7, 8]

# Check if it's O_h-symmetric:
# f(g(s)) should equal g(f(s))
# For weight-1 state s = 2^i:
# f(g(2^i)) = f(2^{perm[i]}) = 2^{antipodal[perm[i]]}
# g(f(2^i)) = g(2^{antipodal[i]}) = 2^{perm[antipodal[i]]}
# These must be equal for all perm, i

sym_ok = True
for g_idx, perm in enumerate(perms):
    for i in range(12):
        left = antipodal[perm[i]]
        right = perm[antipodal[i]]
        if left != right:
            print(f'VIOLATION: g={g_idx}, i={i}: antipodal[perm[{i}]]={left} != perm[antipodal[{i}]]={right}')
            sym_ok = False
            break
    if not sym_ok:
        break

print('Antipodal transposition is O_h-symmetric:', sym_ok)
