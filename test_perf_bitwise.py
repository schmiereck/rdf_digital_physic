import time
import numpy as np

print("Generating transition table using bitwise operations...")
t0 = time.time()
states = np.arange(262144, dtype=np.int32)
perms = [np.random.permutation(18) for _ in range(48)]

table = np.zeros((48, 262144), dtype=np.int32)
for idx, perm in enumerate(perms):
    for i, p in enumerate(perm):
        table[idx] |= ((states >> p) & 1) << i

t1 = time.time()
print(f"Table generated in {t1-t0:.4f} seconds")
