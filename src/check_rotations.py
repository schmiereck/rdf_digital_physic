def _rotate60(state: int) -> int:
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1
    b2 = (state >> 4) & 1
    b3 = (state >> 3) & 1
    b4 = (state >> 2) & 1
    b5 = (state >> 1) & 1
    b6 = (state >> 0) & 1
    return c * 64 + b6 * 32 + b1 * 16 + b2 * 8 + b3 * 4 + b4 * 2 + b5

def _rotate_c2(state: int) -> int:
    return _rotate60(_rotate60(_rotate60(state)))

for s in [4, 6, 72, 96, 68, 70, 8, 32]:
    print(f"state {s:3d}: rot60={_rotate60(s):3d}, rot_c2={_rotate_c2(s):3d}")
