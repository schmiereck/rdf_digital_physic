#!/usr/bin/env python3
import json
with open('archive/iter_219/results/vc_glider_structure.json') as f:
    data = json.load(f)
print('Keys:', list(data.keys()))
print('Structure length:', len(data['structure']))
print('First 5 entries:')
for c in data['structure'][:5]:
    print(f'  {c}')
# Verify center of mass is at (0,0)
rows = [c[0] for c in data['structure']]
cols = [c[1] for c in data['structure']]
print(f'CoM row: {sum(rows)/len(rows):.6f}')
print(f'CoM col: {sum(cols)/len(cols):.6f}')
