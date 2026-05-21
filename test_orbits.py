import time
import numpy as np

print("Generating transition table...")
states = np.arange(262144, dtype=np.int32)
perms = [np.random.permutation(18) for _ in range(48)]

table = np.zeros((48, 262144), dtype=np.int32)
for idx, perm in enumerate(perms):
    for i, p in enumerate(perm):
        table[idx] |= ((states >> p) & 1) << i

print("Finding orbits...")
t0 = time.time()
seen = np.zeros(262144, dtype=bool)
orbits = []
for s in range(262144):
    if seen[s]:
        continue
    # Instead of np.unique, we can use set operations which might be faster or slower:
    # Let's try both or just look at np.unique first
    orb = np.unique(table[:, s])
    seen[orb] = True
    orbits.append(list(orb))

t1 = time.time()
print(f"Orbits found in {t1-t0:.4f} seconds. Num orbits: {len(orbits)}")
