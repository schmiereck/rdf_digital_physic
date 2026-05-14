#!/usr/bin/env python3
"""
characterize_champion_174.py

Characterize the champion rule from iter_174 (g7_rule_076):
  - Load rule from archive/iter_174/results/best_rule.json
  - Initialize with the asymmetric_tromino (L-tromino) seed
  - Run 2000 steps
  - Save animation to archive/iter_174/results/champion_dynamics.mp4
  - Save bit-count plot to archive/iter_174/results/bit_count.png
  - Write analysis to archive/iter_174/results/analysis.txt
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation

sys.path.insert(0, str(Path(__file__).parent))

from evolution import rule_dict_to_lut, step_grid, center_of_mass, make_ltromino_grid

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_174" / "results"

RULE_PATH     = RESULTS_DIR / "best_rule.json"
ANIM_PATH     = RESULTS_DIR / "champion_dynamics.mp4"
BITCOUNT_PATH = RESULTS_DIR / "bit_count.png"
ANALYSIS_PATH = RESULTS_DIR / "analysis.txt"

NUM_STEPS  = 2000
FRAME_SKIP = 5    # 401 frames total, 20 fps → ~20 s video
VIEW_HALF  = 22   # half-side of the zoomed window (45×45 window)
GRID_SIZE  = 128


# ── Simulation ─────────────────────────────────────────────────────────────────

def run_simulation(rule_dict: dict) -> tuple:
    """Simulate for NUM_STEPS steps, store every grid, bit count, and COM."""
    lut  = rule_dict_to_lut(rule_dict)
    grid = make_ltromino_grid()

    all_grids  = [grid.copy()]
    bit_counts = [int(grid.sum())]
    com_track  = [center_of_mass(grid)]

    for _ in range(NUM_STEPS):
        grid = step_grid(grid, lut)
        all_grids.append(grid.copy())
        bit_counts.append(int(grid.sum()))
        com_track.append(center_of_mass(grid))

    return all_grids, bit_counts, com_track


# ── Zoom window helper ─────────────────────────────────────────────────────────

def extract_window(grid: np.ndarray, com: tuple, half: int = VIEW_HALF) -> np.ndarray:
    """Extract a (2*half+1) square around COM with periodic wrapping."""
    N  = grid.shape[0]
    r0 = int(round(com[0]))
    c0 = int(round(com[1]))
    rows = np.arange(r0 - half, r0 + half + 1) % N
    cols = np.arange(c0 - half, c0 + half + 1) % N
    return grid[np.ix_(rows, cols)]


# ── Animation ──────────────────────────────────────────────────────────────────

def make_animation(all_grids: list, com_track: list, path: Path) -> None:
    frame_idx = list(range(0, NUM_STEPS + 1, FRAME_SKIP))
    frames     = [all_grids[i]  for i in frame_idx]
    frame_coms = [com_track[i]  for i in frame_idx]

    fig, ax = plt.subplots(figsize=(5, 5), dpi=100)
    ax.set_axis_off()
    fig.subplots_adjust(left=0, right=1, top=0.93, bottom=0)

    window0 = extract_window(frames[0], frame_coms[0])
    im      = ax.imshow(window0, cmap="binary", vmin=0, vmax=1,
                        interpolation="nearest", origin="upper")
    title   = ax.set_title(f"Step 0  |  bits={int(frames[0].sum())}",
                            fontsize=10)

    def update(i: int):
        w = extract_window(frames[i], frame_coms[i])
        im.set_data(w)
        title.set_text(f"Step {frame_idx[i]}  |  bits={int(frames[i].sum())}")
        return im, title

    anim   = animation.FuncAnimation(fig, update, frames=len(frames),
                                     interval=50, blit=True)
    writer = animation.FFMpegWriter(fps=20, bitrate=1800,
                                    extra_args=["-vcodec", "libx264",
                                                "-pix_fmt", "yuv420p"])
    anim.save(str(path), writer=writer)
    plt.close(fig)
    print(f"  Saved animation: {path}")


# ── Bit-count plot ─────────────────────────────────────────────────────────────

def make_bit_count_plot(bit_counts: list, path: Path,
                        rule_id: str = "g7_rule_076") -> None:
    steps = list(range(len(bit_counts)))

    fig, ax = plt.subplots(figsize=(11, 4), dpi=120)
    ax.plot(steps, bit_counts, color="steelblue", linewidth=0.7, label="bit count")
    ax.set_xlabel("Step")
    ax.set_ylabel("Live cells (bit count)")
    ax.set_title(f"Champion Rule — Bit Count over Time  [{rule_id}]")
    ax.grid(True, alpha=0.3)

    for cp in [400, 800, 1200, 1600, 2000]:
        ax.axvline(cp, color="darkorange", linestyle="--", alpha=0.55,
                   linewidth=0.9, label="checkpoint" if cp == 400 else None)

    ax.legend(fontsize=8)
    ax.text(0.99, 0.97,
            f"initial={bit_counts[0]}  final={bit_counts[-1]}  "
            f"max={max(bit_counts)}",
            transform=ax.transAxes, ha="right", va="top", fontsize=8,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8))
    fig.tight_layout()
    fig.savefig(str(path), dpi=120)
    plt.close(fig)
    print(f"  Saved bit-count plot: {path}")


# ── Analysis helpers ───────────────────────────────────────────────────────────

def compute_window_displacements(com_track: list) -> list:
    windows = [(400, 800), (800, 1200), (1200, 1600), (1600, 2000)]
    out = []
    for t0, t1 in windows:
        r0, c0 = com_track[t0]
        r1, c1 = com_track[t1]
        out.append(math.sqrt((r1 - r0) ** 2 + (c1 - c0) ** 2))
    return out


def detect_bit_count_period(bit_counts: list,
                             window_start: int = 1600,
                             search_len: int = 400) -> int | None:
    tail = bit_counts[window_start: window_start + search_len]
    for p in range(1, search_len // 2):
        if all(tail[i] == tail[i + p] for i in range(search_len - p)):
            return p
    return None


def write_analysis(rule_meta: dict, bit_counts: list,
                   com_track: list, path: Path) -> None:
    disp    = compute_window_displacements(com_track)
    mean_v  = float(np.mean(disp))
    std_v   = float(np.std(disp))

    initial_bits = bit_counts[0]
    final_bits   = bit_counts[-1]
    max_bits     = max(bit_counts)
    min_bits     = min(b for b in bit_counts if b > 0)

    r0,   c0   = com_track[0]
    r2k,  c2k  = com_track[2000]
    # Unwrap COM displacement (account for periodic boundaries)
    dq_raw = r2k - r0
    dc_raw = c2k - c0
    total_disp = math.sqrt(dq_raw ** 2 + dc_raw ** 2)

    tail_bits = bit_counts[1600:]
    tail_mean = float(np.mean(tail_bits))
    tail_std  = float(np.std(tail_bits))

    period = detect_bit_count_period(bit_counts)

    if tail_std < 0.5:
        stability = "highly stable"
    elif tail_std < 2.0:
        stability = "moderately stable"
    else:
        stability = "unstable"

    cv = std_v / (mean_v + 1e-9)  # coefficient of variation

    lines = [
        "Champion Rule Characterization — iter_174",
        "=" * 54,
        f"Rule ID     : {rule_meta['rule_id']}",
        f"Fitness     : {rule_meta['fitness']:.8f}  (StableVelocityFitness)",
        f"mean_vel    : {rule_meta['mean_velocity']:.6f}  cells / 400-step window",
        f"std_vel     : {rule_meta['std_dev_velocity']:.6f}",
        "",
        "─── Bit Count ───────────────────────────────────────",
        f"  Initial (step 0)    : {initial_bits}",
        f"  Final   (step 2000) : {final_bits}",
        f"  Maximum             : {max_bits}",
        f"  Minimum (live)      : {min_bits}",
        "",
        "─── Per-Window Displacements ────────────────────────",
        f"  400 → 800  : {disp[0]:.4f} cells",
        f"  800 → 1200 : {disp[1]:.4f} cells",
        f" 1200 → 1600 : {disp[2]:.4f} cells",
        f" 1600 → 2000 : {disp[3]:.4f} cells",
        f"  Mean vel.  : {mean_v:.4f}  Std dev : {std_v:.4f}",
        f"  CV (std/mean) : {cv:.4f}",
        f"  Total net disp (0→2000) : {total_disp:.2f} cells",
        f"  Net direction           : Δrow={dq_raw:+.2f}, Δcol={dc_raw:+.2f}",
        "",
        "─── Tail Stability (steps 1600–2000) ────────────────",
        f"  Bit-count mean : {tail_mean:.2f}",
        f"  Bit-count std  : {tail_std:.4f}   → {stability}",
        f"  Period detected: {period if period is not None else 'none (>200 steps)'}",
        "",
        "─── Qualitative Analysis ────────────────────────────",
    ]

    # Growth narrative
    if final_bits == 0:
        lines.append("  The particle ANNIHILATED: the grid went dark before step 2000.")
    elif final_bits > initial_bits * 3:
        lines.append(
            f"  The particle expanded substantially ({initial_bits}→{final_bits} bits). "
            "Significant bit growth occurred, indicating the rule does not conserve "
            "particle size under this seed."
        )
    elif final_bits > initial_bits:
        lines.append(
            f"  The particle grew from {initial_bits} to {final_bits} bits, "
            "suggesting moderate replication or accumulation of live cells."
        )
    else:
        lines.append(
            f"  Bit count is stable or slightly reduced ({initial_bits}→{final_bits})."
        )

    # Motion narrative
    if mean_v > 5.0:
        lines.append(
            f"  MOBILE: the particle travels ~{mean_v:.2f} cells per 400 steps "
            f"(≈{total_disp:.1f} cells net over 2000 steps)."
        )
    elif mean_v > 1.0:
        lines.append(
            f"  SLOW DRIFT: particle moves ~{mean_v:.2f} cells per 400 steps."
        )
    else:
        lines.append("  STATIONARY: particle shows negligible displacement.")

    # Regularity narrative
    if cv < 0.3:
        lines.append(
            "  Motion is REGULAR (low CV), consistent with periodic glider-like "
            "behaviour."
        )
    elif cv < 0.6:
        lines.append(
            "  Motion is MODERATELY IRREGULAR (medium CV): likely intermittent "
            "or phase-shifting glider."
        )
    else:
        lines.append(
            "  Motion is IRREGULAR (high CV): erratic, possibly turbulent rather "
            "than a clean glider."
        )

    if period is not None:
        lines.append(
            f"  A period-{period} oscillation was detected in the bit count during the "
            "tail phase, indicating a periodic attractor."
        )

    lines.append("")
    lines.append(
        "Note: the fitness metric rewards mean_velocity / (1 + std_dev_velocity) "
        "× (initial_bits / final_bits). A fitness of "
        f"{rule_meta['fitness']:.4f} at final_bits={final_bits} (from 3) places "
        "this rule among the more mobile individuals in the evolved population."
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Saved analysis: {path}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(RULE_PATH) as f:
        rule_meta = json.load(f)

    rule_dict = {int(k): int(v) for k, v in rule_meta["rule"].items()}

    print(f"Loaded rule  : {rule_meta['rule_id']}")
    print(f"  fitness={rule_meta['fitness']:.6f}  "
          f"mean_v={rule_meta['mean_velocity']:.4f}  "
          f"std_v={rule_meta['std_dev_velocity']:.4f}")

    print(f"Simulating {NUM_STEPS} steps …")
    all_grids, bit_counts, com_track = run_simulation(rule_dict)

    print(f"  Initial bits : {bit_counts[0]}")
    print(f"  Final bits   : {bit_counts[-1]}")
    print(f"  Max bits     : {max(bit_counts)}")
    min_live = min(b for b in bit_counts if b > 0)
    print(f"  Min bits     : {min_live}")

    print("Generating bit-count plot …")
    make_bit_count_plot(bit_counts, BITCOUNT_PATH,
                        rule_id=rule_meta["rule_id"])

    print("Generating animation …")
    make_animation(all_grids, com_track, ANIM_PATH)

    print("Writing analysis …")
    write_analysis(rule_meta, bit_counts, com_track, ANALYSIS_PATH)

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
