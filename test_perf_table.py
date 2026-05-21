import time
import numpy as np

print("Generating transition table...")
t0 = time.time()
powers = 2 ** np.arange(18, dtype=np.int32)
bits = np.zeros((262144, 18), dtype=np.uint8)
for i in range(18):
    bits[:, i] = (np.arange(262144) >> i) & 1

# Generate 48 random perms
perms = [np.random.permutation(18) for _ in range(48)]

# Preallocate transition table
table = np.zeros((48, 262144), dtype=np.int32)
for idx, perm in enumerate(perms):
    table[idx, :] = bits[:, perm] @ powers

t1 = time.time()
print(f"Table generated in {t1-t0:.4f} seconds")
