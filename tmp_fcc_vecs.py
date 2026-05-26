import numpy as np

# Replicate the fcc_neighbor_vectors function
vecs = []
for i in range(3):
    for j in range(i + 1, 3):
        for si in (-1, 1):
            for sj in (-1, 1):
                v = [0, 0, 0]
                v[i] = si
                v[j] = sj
                vecs.append(tuple(v))

for i, v in enumerate(vecs):
    print(f'ch{i}: {v}')

print()
print('Antipodal pairs:')
for i in range(12):
    neg = tuple(-np.array(vecs[i]))
    for j in range(12):
        if vecs[j] == neg:
            print(f'  {i} <-> {j}')
