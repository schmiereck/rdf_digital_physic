import json
r = json.load(open("archive/iter_179/results/champion_rule.json"))
c = r["chromosome"]
def rot_c2(s):
    center = (s >> 6) & 1
    b5 = (s >> 5) & 1
    b4 = (s >> 4) & 1
    b3 = (s >> 3) & 1
    b2 = (s >> 2) & 1
    b1 = (s >> 1) & 1
    b0 = (s >> 0) & 1
    return (center << 6) | (b2 << 5) | (b1 << 4) | (b0 << 3) | (b5 << 2) | (b4 << 1) | b3

symmetric = True
for s in range(128):
    if c[s] != c[rot_c2(s)]:
        print(f"Broken: s={s} c[s]={c[s]} vs c[rot_c2(s)]={c[rot_c2(s)]}")
        symmetric = False
print("Is C2-symmetric:", symmetric)
