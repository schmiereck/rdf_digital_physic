#!/usr/bin/env python3
"""
characterize_rule.py

Rigorously characterize a champion CA rule from a JSON file.

Runs a long simulation from a minimal 3-bit seed, tracks centre-of-mass
and bit count at every step, calculates velocity and net displacement,
generates a GIF, and prints a YAML metrics block.

Usage
-----
    python src/characterize_rule.py \
      --rule_file=archive/iter_213.10/results/champion_rule.json \
      --steps=1000 \
      --output_gif=archive/iter_213.10/results/long_run.gif
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from evolution import center_of_mass, rule_dict_to_lut, step_grid

PROJECT_ROOT = Path(__file__).parent.parent

# ── Grid helpers ───────────────────────────────────────────────────────────────

def make_particle_grid(particle: list, grid_size: int = 128) -> np.ndarray:
    """Return a zero grid with *particle* (dr, dc offsets) centred on the grid."""
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    centre = grid_size // 2
    for item in particle:
        dr, dc = int(item[0]), int(item[1])
        grid[(centre + dr) % grid_size, (centre + dc) % grid_size] = 1
    return grid


# ── Simulation ─────────────────────────────────────────────────────────────────

def run_simulation(
    rule_dict: dict,
    seed_particle: list,
    steps: int,
    grid_size: int = 128,
    frame_every: int = 5,
) -> tuple[list, list, list]:
    """Simulate *steps* steps; return (com_history, bit_history, frames).

    frames is a list of (step_index, grid_copy) sampled every *frame_every* steps.
    """
    lut  = rule_dict_to_lut(rule_dict)
    grid = make_particle_grid(seed_particle, grid_size)

    com_history: list[tuple[float, float]] = [center_of_mass(grid)]
    bit_history: list[int]                 = [int(grid.sum())]
    frames: list[tuple[int, np.ndarray]]   = [(0, grid.copy())]

    for t in range(1, steps + 1):
        grid = step_grid(grid, lut)
        com_history.append(center_of_mass(grid))
        bit_history.append(int(grid.sum()))
        if t % frame_every == 0 or t == steps:
            frames.append((t, grid.copy()))

    return com_history, bit_history, frames


# ── Metrics ────────────────────────────────────────────────────────────────────

def compute_metrics(
    com_history: list,
    bit_history: list,
    steps: int,
) -> dict:
    initial_com = com_history[0]
    final_com   = com_history[-1]

    dx = final_com[0] - initial_com[0]
    dy = final_com[1] - initial_com[1]
    net_displacement = math.sqrt(dx * dx + dy * dy)
    avg_velocity     = net_displacement / steps  # cells/step

    bits = np.array(bit_history, dtype=np.int32)
    bit_stable = bool(np.all(bits == bits[0]))
    bit_min    = int(bits.min())
    bit_max    = int(bits.max())
    bit_final  = int(bits[-1])

    # Per-step CoM displacement (instantaneous speed)
    com_arr    = np.array(com_history, dtype=np.float64)
    step_disp  = np.sqrt(np.sum(np.diff(com_arr, axis=0) ** 2, axis=1))
    mean_step_disp       = float(np.mean(step_disp))
    last100_step_disp    = float(np.mean(step_disp[-100:])) if len(step_disp) >= 100 else mean_step_disp

    # Drift per 100-step window — detects periodic glider motion
    drift_per_100: list[float] = []
    for i in range(0, len(com_history) - 100, 100):
        c0 = com_history[i]
        c1 = com_history[i + 100]
        d  = math.sqrt((c1[0] - c0[0]) ** 2 + (c1[1] - c0[1]) ** 2)
        drift_per_100.append(round(d, 6))

    # Stability label
    if bit_final == 0:
        stability = "annihilated"
    elif not bit_stable:
        stability = "unstable"
    else:
        stability = "stable"

    # Classification
    if avg_velocity >= 0.05 and bit_stable:
        classification = "true_glider_candidate"
    elif avg_velocity >= 0.001 and bit_stable:
        classification = "slow_drifter"
    elif avg_velocity < 0.001 and bit_stable:
        classification = "oscillator_or_still_life"
    else:
        classification = "unstable_or_annihilated"

    return {
        "initial_com":                  [round(x, 6) for x in initial_com],
        "final_com":                    [round(x, 6) for x in final_com],
        "net_displacement":             round(net_displacement, 6),
        "avg_velocity_cells_per_step":  round(avg_velocity, 8),
        "mean_step_displacement":       round(mean_step_disp, 8),
        "last100_mean_step_disp":       round(last100_step_disp, 8),
        "drift_per_100_steps":          drift_per_100,
        "bit_stable":                   bit_stable,
        "bit_min":                      bit_min,
        "bit_max":                      bit_max,
        "bit_final":                    bit_final,
        "stability":                    stability,
        "classification":               classification,
    }


# ── GIF ────────────────────────────────────────────────────────────────────────

def render_gif(
    frames: list[tuple[int, np.ndarray]],
    gif_path: Path,
    grid_size: int,
    title: str = "Champion rule — long run",
) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.animation as animation
    import matplotlib.pyplot as plt

    # Show a 48×48 crop centred on the grid (particle stays near centre)
    half  = 24
    ctr   = grid_size // 2
    r0, r1 = ctr - half, ctr + half
    c0, c1 = ctr - half, ctr + half

    def crop(g: np.ndarray) -> np.ndarray:
        return g[r0:r1, c0:c1]

    fig, ax = plt.subplots(figsize=(5, 5), dpi=80)
    ax.set_title(title, fontsize=9)
    ax.set_xlabel("col")
    ax.set_ylabel("row")
    ax.set_xlim(0, 2 * half)
    ax.set_ylim(0, 2 * half)

    img = ax.imshow(
        crop(frames[0][1]),
        origin="upper", interpolation="nearest",
        cmap="hot", vmin=0, vmax=1,
        extent=[0, 2 * half, 2 * half, 0],
    )
    step_text = ax.text(
        0.02, 0.97, f"step={frames[0][0]}",
        transform=ax.transAxes, color="white", fontsize=9, va="top",
    )

    def update(i: int):
        s, g = frames[i]
        img.set_data(crop(g))
        step_text.set_text(f"step={s}")
        return img, step_text

    ani = animation.FuncAnimation(
        fig, update, frames=len(frames), interval=40, blit=True,
    )
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    ani.save(str(gif_path), writer="pillow", fps=20)
    plt.close(fig)
    print(f"  GIF saved: {gif_path}  ({len(frames)} frames)")


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Characterize a champion CA rule")
    parser.add_argument("--rule_file",  required=True, help="Path to champion_rule.json")
    parser.add_argument("--steps",      type=int, default=1000)
    parser.add_argument("--output_gif", required=True, help="Output GIF path")
    parser.add_argument("--grid_size",  type=int, default=128)
    args = parser.parse_args()

    rule_file = Path(args.rule_file)
    if not rule_file.is_absolute():
        rule_file = PROJECT_ROOT / rule_file

    gif_path = Path(args.output_gif)
    if not gif_path.is_absolute():
        gif_path = PROJECT_ROOT / gif_path

    # Load rule
    print(f"Loading rule from: {rule_file}")
    with open(rule_file, encoding="utf-8") as f:
        data = json.load(f)

    rule_dict     = {str(k): int(v) for k, v in data["rule_dict"].items()}
    seed_particle = data.get("seed_particle", [[0, 0], [0, 1], [1, 1]])
    print(f"Seed particle  : {seed_particle}")
    print(f"Non-identity entries in rule_dict: {len(rule_dict)}")

    # Simulate
    print(f"Running {args.steps} steps on {args.grid_size}×{args.grid_size} grid …")
    com_history, bit_history, frames = run_simulation(
        rule_dict, seed_particle, args.steps, args.grid_size, frame_every=5,
    )
    print(f"Simulation done. Frames captured: {len(frames)}")

    # Metrics
    metrics = compute_metrics(com_history, bit_history, args.steps)

    # Print human-readable summary
    print("\n=== Characterization Results ===")
    for k, v in metrics.items():
        print(f"  {k:<38s}: {v}")

    # Render GIF
    print(f"\nRendering GIF ({len(frames)} frames) …")
    render_gif(
        frames, gif_path, args.grid_size,
        title=f"Champion (steps=0–{args.steps}) [{metrics['classification']}]",
    )

    # YAML block (required by orchestrator)
    print("\n```yaml")
    print(f"status: ok")
    print(f"artifacts:")
    print(f"  - {str(gif_path.relative_to(PROJECT_ROOT)).replace(chr(92), '/')}")
    print(f"  - src/characterize_rule.py")
    print(f"metrics:")
    print(f"  net_displacement: {metrics['net_displacement']}")
    print(f"  avg_velocity_cells_per_step: {metrics['avg_velocity_cells_per_step']}")
    print(f"  bit_stable: {str(metrics['bit_stable']).lower()}")
    print(f"  bit_min: {metrics['bit_min']}")
    print(f"  bit_max: {metrics['bit_max']}")
    print(f"  bit_final: {metrics['bit_final']}")
    print(f"  mean_step_displacement: {metrics['mean_step_displacement']}")
    print(f"  last100_mean_step_disp: {metrics['last100_mean_step_disp']}")
    drift_str = "[" + ", ".join(str(d) for d in metrics['drift_per_100_steps']) + "]"
    print(f"  drift_per_100_steps: {drift_str}")
    print(f"log_excerpt: |")
    print(f"  initial_com: {metrics['initial_com']}")
    print(f"  final_com: {metrics['final_com']}")
    print(f"  net_displacement: {metrics['net_displacement']}")
    print(f"  avg_velocity: {metrics['avg_velocity_cells_per_step']} cells/step")
    print(f"  bit_stable: {metrics['bit_stable']}")
    print(f"  stability: {metrics['stability']}")
    print(f"  classification: {metrics['classification']}")
    print(f"  drift_per_100: {metrics['drift_per_100_steps']}")
    print(f"experimenter_view: |")
    view = _build_experimenter_view(metrics, args.steps)
    for line in view.split("\n"):
        print(f"  {line}")
    print(f"notes: long_run characterization of champion rule over {args.steps} steps")
    print("```")

    return 0


def _build_experimenter_view(metrics: dict, steps: int) -> str:
    cls  = metrics["classification"]
    vel  = metrics["avg_velocity_cells_per_step"]
    disp = metrics["net_displacement"]
    stable = metrics["bit_stable"]
    drift  = metrics["drift_per_100_steps"]

    lines = [
        f"Classification: {cls}",
        f"Net displacement over {steps} steps: {disp:.6f} cells.",
        f"Average velocity: {vel:.8f} cells/step.",
    ]
    if stable:
        lines.append("Bit count is perfectly stable (all {bits} bits preserved throughout).".format(
            bits=metrics["bit_min"]))
    else:
        lines.append(f"Bit count is NOT stable: min={metrics['bit_min']}, max={metrics['bit_max']}, final={metrics['bit_final']}.")

    if drift:
        consistent = max(drift) - min(drift) < 0.01 * max(drift) + 0.001
        lines.append(f"Drift per 100-step window: {drift}.")
        if consistent and max(drift) > 0.01:
            lines.append("Drift is CONSISTENT across windows — suggests a true glider.")
        elif max(drift) < 0.01:
            lines.append("Drift is near zero in all windows — likely a still life or oscillator.")
        else:
            lines.append("Drift is INCONSISTENT across windows — likely a slow or oscillating drifter.")

    if cls == "slow_drifter":
        lines.append("VERDICT: slow drifter — moves by less than 0.05 cells/step but is not stationary.")
    elif cls == "oscillator_or_still_life":
        lines.append("VERDICT: oscillator or still life — no net translation detected.")
    elif cls == "true_glider_candidate":
        lines.append("VERDICT: true glider candidate — significant sustained translation.")
    else:
        lines.append("VERDICT: unstable / annihilated.")

    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
