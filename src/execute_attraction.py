import sys
import os
import io

# Setup paths
sys.path.insert(0, os.path.abspath('src'))

# Import and redirect stdout to capture output
import run_dynamic_attraction
f = io.StringIO()
sys.stdout = f
run_dynamic_attraction.main()
sys.stdout = sys.__stdout__

# Write output to results
out_dir = 'archive/iter_230/results'
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, 'output.txt'), 'w') as out_f:
    out_f.write(f.getvalue())
print("Simulation completed programmatically!")
