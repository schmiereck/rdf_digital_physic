import numpy as np

perm = np.random.permutation(18)
state = 12345

# Method 1: scalar pull-back
def apply_channel_perm(perm, state):
    new = 0
    for i in range(18):
        if (state >> perm[i]) & 1:
            new |= 1 << i
    return new

res1 = apply_channel_perm(perm, state)

# Method 2: bitwise vectorized
states = np.arange(262144, dtype=np.int32)
res2 = np.zeros(262144, dtype=np.int32)
for i, p in enumerate(perm):
    res2 |= ((states >> p) & 1) << i

print("Match:", res1 == res2[state])
