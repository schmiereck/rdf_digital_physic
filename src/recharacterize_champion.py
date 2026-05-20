#!/usr/bin/env python3
"""
recharacterize_champion.py  —  Recalculate fitness and per-window velocities
of the discovered v<c glider, and re-generate its output files.
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from run_evolution_exp_222 import (
    _simulate_history_from_lut,
    render_champion_gif,
    characterise_champion,
    _FITNESS_FN,
)
from evolution import rule_dict_to_lut

# ── Load champion rule ──────────────────────────────────────────────────────

OUTPUT_DIR = PROJECT_ROOT / "archive" / "iter_222" / "results"
champ_json_path = OUTPUT_DIR / "champion_rule_perfect.json"

with open(champ_json_path) as f:
    payload = json.load(f)

rule_dict = {int(k): int(v) for k, v in payload["rule_dict"].items()}
print("Loaded rule dict with", len(rule_dict), "entries.")

# ── Simulate and evaluate ──────────────────────────────────────────────────

lut = rule_dict_to_lut(rule_dict)
hist = _simulate_history_from_lut(lut, steps=500)
new_fitness = _FITNESS_FN(hist)
print(f"Recalculated fitness (trigonometric CoM): {new_fitness}")

# ── Update champion JSON ───────────────────────────────────────────────────

payload["fitness"] = new_fitness
with open(champ_json_path, "w") as f:
    json.dump(payload, f, indent=2)
print("Updated champion_rule_perfect.json")

# ── Re-render GIF and trajectory analysis ──────────────────────────────────

gif_path = OUTPUT_DIR / "champion_vc_glider_perfect.gif"
render_champion_gif(rule_dict, gif_path)

txt_path = OUTPUT_DIR / "trajectory_analysis.txt"
char = characterise_champion(rule_dict, txt_path, new_fitness)
print("Characterisation complete:")
print(char)
