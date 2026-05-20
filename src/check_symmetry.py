import json
import numpy as np
from pathlib import Path

# Load original rule
champion_path = Path("archive/iter_179/results/champion_rule.json")
with open(champion_path, "r") as f:
    champion = json.load(f)

chrom = np.array(champion["chromosome"], dtype=np.uint8)

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

symmetric = True
for s in range(128):
    rot = _rotate_c2(s)
    if chrom[s] != chrom[rot]:
        print(f"Asymmetry: chrom[{s}] = {chrom[s]} vs chrom[{rot}] = {chrom[rot]}")
        symmetric = False

if symmetric:
    print("The chromosome is perfectly C2-symmetric!")
else:
    print("The chromosome is NOT C2-symmetric!")
