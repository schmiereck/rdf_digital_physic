import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from evolution import _rotate_c2

r = json.load(open("archive/iter_179/results/champion_rule.json"))
c = r["chromosome"]

symmetric = True
for s in range(128):
    if c[s] != c[_rotate_c2(s)]:
        print(f"Broken: s={s} c[s]={c[s]} vs c[_rotate_c2(s)]={c[_rotate_c2(s)]}")
        symmetric = False
print("Is C2-symmetric:", symmetric)
