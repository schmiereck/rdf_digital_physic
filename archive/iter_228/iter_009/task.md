Write the following code to `src/analyze_d4_collision_18.py`:

```python
import numpy as np
import json
import os
from src.engine_d4_spacetime_18 import (
    generate_symmetric_lut, compute_momentum, PROJECTED_VECTORS, NUM_STATES
)

def main():
    print("Running D4 18-Channel Collision Analysis...")
    lut = generate_symmetric_lut(seed=42)
    
    total_scattering = 0
    weight_total = [0] * 19
    weight_scattering = [0] * 19
    
    for s in range(NUM_STATES):
        w = bin(s).count("1")
        weight_total[w] += 1
        if lut[s] != s:
            total_scattering += 1
            weight_scattering[w] += 1
            
    print(f"Total states: {NUM_STATES}")
    print(f"Scattering states: {total_scattering} ({total_scattering/NUM_STATES*100:.2f}%)")
    
    head_on_states = []
    for s in range(NUM_STATES):
        if bin(s).count("1") == 2:
            mom = compute_momentum(s)
            if mom == (0, 0, 0):
                head_on_states.append(s)
                
    print(f"Found {len(head_on_states)} head-on 2-bit states.")
    
    tt_to_tt = 0
    tt_to_ss = 0
    ss_to_tt = 0
    ss_to_ss = 0
    
    for s in head_on_states:
        ch1, ch2 = [i for i in range(18) if (s >> i) & 1]
        in_type = "TT" if (ch1 < 6 and ch2 < 6) else "SS"
        
        s_out = int(lut[s])
        ch1_out, ch2_out = [i for i in range(18) if (s_out >> i) & 1]
        out_type = "TT" if (ch1_out < 6 and ch2_out < 6) else "SS"
        
        if in_type == "TT" and out_type == "TT":
            tt_to_tt += 1
        elif in_type == "TT" and out_type == "SS":
            tt_to_ss += 1
        elif in_type == "SS" and out_type == "TT":
            ss_to_tt += 1
        elif in_type == "SS" and out_type == "SS":
            ss_to_ss += 1
            
    print(f"TT -> TT: {tt_to_tt}")
    print(f"TT -> SS: {tt_to_ss}")
    print(f"SS -> TT: {ss_to_tt}")
    print(f"SS -> SS: {ss_to_ss}")
    
    # Save results to a file
    os.makedirs("archive/iter_228/results", exist_ok=True)
    with open("archive/iter_228/results/collision_output.txt", "w") as f:
        f.write(f"Total states: {NUM_STATES}\\n")
        f.write(f"Scattering states: {total_scattering}\\n")
        f.write(f"Head-on 2-bit states: {len(head_on_states)}\\n")
        f.write(f"TT -> TT: {tt_to_tt}\\n")
        f.write(f"TT -> SS: {tt_to_ss}\\n")
        f.write(f"SS -> TT: {ss_to_tt}\\n")
        f.write(f"SS -> SS: {ss_to_ss}\\n")

if __name__ == '__main__':
    main()
```

Run this command exactly: `python src/analyze_d4_collision_18.py`. Do not write any mock report, just write the file, execute it, write the results to `archive/iter_228/results/collision_output.txt`, and finish. I will read that file.