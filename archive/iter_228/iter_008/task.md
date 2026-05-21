Create the file `src/analyze_d4_collision_18.py` with the following code:

```python
#!/usr/bin/env python3
\"\"\"analyze_d4_collision_18.py — Analyze the physical properties of the 18-channel D4 LGCA.
\"\"\"

import numpy as np
import json
import os
from src.engine_d4_spacetime_18 import (
    generate_symmetric_lut, compute_momentum, PROJECTED_VECTORS, NUM_STATES
)

def main():
    print("=== D4 18-Channel Collision Analysis ===")
    
    # Generate the symmetric LUT with seed 42
    print("Generating LUT with seed 42...")
    lut = generate_symmetric_lut(seed=42)
    
    # 1. Scattering vs Identity analysis
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
    print(f"Scattering (non-identity) states: {total_scattering} ({total_scattering/NUM_STATES*100:.2f}%)")
    
    print("\nScattering breakdown by Hamming weight:")
    print("| Weight | Total States | Scattering States | Scattering % |")
    print("|--------|--------------|-------------------|--------------|")
    for w in range(19):
        tot = weight_total[w]
        sc = weight_scattering[w]
        pct = (sc / tot * 100) if tot > 0 else 0.0
        print(f"| {w:<6} | {tot:<12} | {sc:<17} | {pct:<12.2f}% |")
        
    # 2. 2-Bit Head-on Collision Analysis
    print("\nAnalyzing head-on 2-bit collisions...")
    head_on_states = []
    for s in range(NUM_STATES):
        if bin(s).count("1") == 2:
            mom = compute_momentum(s)
            if mom == (0, 0, 0):
                head_on_states.append(s)
                
    print(f"Found {len(head_on_states)} head-on 2-bit states.")
    
    # Classify head-on states
    tt_to_tt = 0
    tt_to_ss = 0
    ss_to_tt = 0
    ss_to_ss = 0
    
    transitions = []
    
    for s in head_on_states:
        # Input channels
        ch1, ch2 = [i for i in range(18) if (s >> i) & 1]
        in_type = "TT" if (ch1 < 6 and ch2 < 6) else "SS"
        
        # Output state
        s_out = int(lut[s])
        ch1_out, ch2_out = [i for i in range(18) if (s_out >> i) & 1]
        out_type = "TT" if (ch1_out < 6 and ch2_out < 6) else "SS"
        
        # Match type
        if in_type == "TT" and out_type == "TT":
            tt_to_tt += 1
        elif in_type == "TT" and out_type == "SS":
            tt_to_ss += 1
        elif in_type == "SS" and out_type == "TT":
            ss_to_tt += 1
        elif in_type == "SS" and out_type == "SS":
            ss_to_ss += 1
            
        transitions.append({
            "input_state": s,
            "input_channels": [ch1, ch2],
            "input_type": in_type,
            "output_state": s_out,
            "output_channels": [ch1_out, ch2_out],
            "output_type": out_type
        })
        
    print("\nHead-on 2-bit transition statistics:")
    print(f"  TT -> TT (Light-to-Light scattering):  {tt_to_tt}")
    print(f"  TT -> SS (Light-to-Matter creation):  {tt_to_ss}")
    print(f"  SS -> TT (Matter-to-Light annihilation): {ss_to_tt}")
    print(f"  SS -> SS (Matter-to-Matter scattering): {ss_to_ss}")
    
    # Save report
    results_dir = "archive/iter_228/results"
    os.makedirs(results_dir, exist_ok=True)
    report_path = os.path.join(results_dir, "collision_analysis.json")
    
    report_data = {
        "summary": {
            "total_states": NUM_STATES,
            "scattering_states": total_scattering,
            "scattering_percentage": total_scattering / NUM_STATES,
            "weight_breakdown": {
                str(w): {
                    "total": weight_total[w],
                    "scattering": weight_scattering[w],
                    "percentage": weight_scattering[w] / weight_total[w] if weight_total[w] > 0 else 0.0
                } for w in range(19)
            }
        },
        "head_on_2bit": {
            "total_count": len(head_on_states),
            "tt_to_tt": tt_to_tt,
            "tt_to_ss": tt_to_ss,
            "ss_to_tt": ss_to_tt,
            "ss_to_ss": ss_to_ss,
            "transitions": transitions
        }
    }
    
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=4)
    print(f"\nSaved detailed analysis report to {report_path}")

if __name__ == "__main__":
    main()
```

Run the file with `python src/analyze_d4_collision_18.py` and print the complete terminal output. Success criterion: stdout contains head-on transition statistics.