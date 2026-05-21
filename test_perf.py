import time
import numpy as np

print("Starting test...")
powers = 2 ** np.arange(18, dtype=np.int32)
bits = np.zeros((262144, 18), dtype=np.uint8)
for i in range(18):
    bits[:, i] = (np.arange(262144) >> i) & 1

t0 = time.time()
perm = np.random.permutation(18)
permuted = bits[:, perm] @ powers
t1 = time.time()
print(f"Single perm in {t1-t0:.4f} seconds")
