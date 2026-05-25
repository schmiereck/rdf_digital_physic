import json, numpy as np
with open('archive/iter_224/results/glider_00_lut08_sub03.json') as f:
    ref = json.load(f)
lut = np.array(ref['lut'], dtype=np.uint16)
print('LUT shape:', lut.shape)
for s in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]:
    out = lut[s]
    pop_in = bin(s).count('1')
    pop_out = bin(out).count('1')
    print(f'lut[{s}] = {out}, pop_in={pop_in}, pop_out={pop_out}')

conserved = all(bin(s).count('1') == bin(int(lut[s])).count('1') for s in range(4096))
print('Fully conserved:', conserved)
# Check for 2+ bit states that map to themselves
identity_count = sum(lut[s] == s for s in range(4096))
print('Identity mappings:', identity_count)
# Check 2-bit states
for s in range(4096):
    if bin(s).count('1') == 2:
        out = int(lut[s])
        print(f'2-bit {s} -> {out} (same={out==s})')
        if s > 10:
            break
# Check what happens with weight-2 inputs that travel together
for ch1, ch2 in [(5,6)]:
    s = (1<<ch1) | (1<<ch2)
    out = int(lut[s])
    print(f'ch({ch1},{ch2}) -> packed={s} -> {out} ({bin(out)})')
