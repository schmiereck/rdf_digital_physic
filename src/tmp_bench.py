import numpy as np
import time
from synchronous_ca_fcc import simulate
L=40
grid = np.zeros((L,L,L), dtype=np.uint8)
grid[20,20,20]=1
grid[21,20,20]=1
B={3,4}
S={2,3}
t0=time.time()
res = simulate(grid, B, S, steps=200)
t1=time.time()
print('Time:', t1-t0)
print('Survival:', res['survival_time'])
print('Bits:', res['bit_counts'][-1])
