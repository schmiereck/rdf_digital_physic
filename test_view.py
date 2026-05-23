import json

with open("archive/iter_239/results/scattering_sweep_results.json") as f:
    data = json.load(f)

# Sort results by delta_y desc (from 4 down to -4), then by delta_t asc (from 0 to 12)
results_by_y = {}
for r in data["results"]:
    dy = r["delta_y"]
    if dy not in results_by_y:
        results_by_y[dy] = {}
    results_by_y[dy][r["delta_t"]] = r["outcome"]

for dy in sorted(results_by_y.keys(), reverse=True):
    row_outcomes = [results_by_y[dy][dt] for dt in sorted(results_by_y[dy].keys())]
    print(f"dy = {dy:2d}: {row_outcomes}")
