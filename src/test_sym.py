import sys
sys.path.insert(0, 'src')
from search_3d_gliders import get_oh_permutations

PAIRS = [(0, 3), (1, 2), (4, 7), (5, 6), (8, 11), (9, 10)]
trans = [0] * 12
for a, b in PAIRS:
    trans[a] = b
    trans[b] = a

perms = get_oh_permutations(verbose=False)
print('perms:', len(perms))

sym_ok = True
for g_idx, perm in enumerate(perms):
    for i in range(12):
        left = trans[perm[i]]
        right = perm[trans[i]]
        if left != right:
            sym_ok = False
            print(f'Violation at g={g_idx}, i={i}: trans[perm[i]]={left}, perm[trans[i]]={right}')
            break
    if not sym_ok:
        break

print(f'Symmetric: {sym_ok}')
