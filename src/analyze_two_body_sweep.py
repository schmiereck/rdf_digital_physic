#!/usr/bin/env python3
"""analyze_two_body_sweep.py — Post-hoc analysis of the closed-loop two-body
attraction sweep stored in ``archive/iter_233/results/closed_loop_attraction.json``.

The script answers four questions:

1. Which configuration achieved the maximum mutual deflection
   (``defl_Y1 - defl_Y2``)?
2. Did any configuration actually pull the gliders together — i.e. is
   ``mutual_attraction`` strictly positive?  How does the 120-step long run
   compare against the 80-step best entry?
3. Render a clean trajectory plot and table (Y1, Y2, separation) for the
   best/long-run trajectory and save them to disk.
4. Inspect the location of the optimum within the parameter grid to decide
   whether a finer or wider sweep is warranted.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
JSON_PATH = os.path.join(REPO, "archive", "iter_233", "results",
                         "closed_loop_attraction.json")
OUT_DIR = os.path.join(REPO, "archive", "iter_233", "results")
PLOT_PATH = os.path.join(OUT_DIR, "best_trajectory.png")
TABLE_PATH = os.path.join(OUT_DIR, "best_trajectory.csv")
REPORT_PATH = os.path.join(OUT_DIR, "two_body_sweep_analysis.txt")


def section(title: str) -> None:
    bar = "=" * 96
    print(bar)
    print(title)
    print(bar)


def load_results() -> dict[str, Any]:
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def find_best(all_results: list[dict[str, Any]]) -> dict[str, Any]:
    return max(all_results, key=lambda r: (r["mutual_attraction"], r["stable"]))


def report_overview(data: dict[str, Any]) -> None:
    meta = data["meta"]
    grid = data["param_grid"]
    summary = data["sweep_summary"]
    section("DATASET OVERVIEW")
    print(f"  source              : {JSON_PATH}")
    print(f"  grid size L         : {meta['L']}")
    print(f"  short sweep steps   : {meta['steps']}")
    print(f"  long-run steps      : {meta['long_steps']}")
    print(f"  glider 1 seed (cy)  : {meta['cy1']}")
    print(f"  glider 2 seed (cy)  : {meta['cy2']}")
    print(f"  initial separation  : {meta['cy2'] - meta['cy1']}")
    print(f"  lut_seed/sub_seed   : {meta['lut_seed']} / {meta['sub_seed']}")
    print(f"  expected total bits : {meta['expected_total_bits']} "
          f"({meta['expected_bits_per_glider']} per glider)")
    print(f"  total configs       : {summary['total_configurations']}")
    print(f"  stable configs      : {summary['stable_count']}")
    print()
    print("  parameter grid:")
    for k, v in grid.items():
        print(f"    {k:<10}: {v}")
    print()


def report_question1_best(data: dict[str, Any], best: dict[str, Any]) -> None:
    section("Q1. BEST CONFIGURATION (max mutual deflection)")
    print(f"  alpha     = {best['alpha']}")
    print(f"  threshold = {best['threshold']}")
    print(f"  gamma     = {best['gamma']}")
    print(f"  kappa     = {best['kappa']}")
    print(f"  eta       = {best['eta']}")
    print(f"  Y1_final  = {best['Y1_final']:+.4f}  (seed cy1={data['meta']['cy1']})")
    print(f"  Y2_final  = {best['Y2_final']:+.4f}  (seed cy2={data['meta']['cy2']})")
    print(f"  defl_Y1   = {best['defl_Y1']:+.4f}")
    print(f"  defl_Y2   = {best['defl_Y2']:+.4f}")
    print(f"  mutual    = {best['mutual_attraction']:+.4f}  (defl_Y1 - defl_Y2)")
    print(f"  stable    = {best['stable']}")
    print(f"  steps OK  = {best['n_steps_completed']}/{data['meta']['steps']}")
    print()


def report_question2_attraction(data: dict[str, Any]) -> None:
    section("Q2. DID ANY CONFIG ACHIEVE MUTUAL ATTRACTION?")

    all_results = data["all_results"]
    positives = [r for r in all_results if r["mutual_attraction"] > 0.0]
    zeros = [r for r in all_results if r["mutual_attraction"] == 0.0]
    negatives = [r for r in all_results if r["mutual_attraction"] < 0.0]

    print(f"  mutual_attraction > 0  : {len(positives)} / {len(all_results)}")
    print(f"  mutual_attraction == 0 : {len(zeros)} / {len(all_results)}")
    print(f"  mutual_attraction < 0  : {len(negatives)} / {len(all_results)}")
    print()
    print("  distinct mutual_attraction values (count):")
    for value, count in sorted(Counter(round(r['mutual_attraction'], 6)
                                       for r in all_results).items()):
        print(f"    {value:+.4f}  ->  {count}")
    print()

    cy1, cy2 = data["meta"]["cy1"], data["meta"]["cy2"]
    init_sep = cy2 - cy1
    print(f"  separation Y2-Y1 at step {data['meta']['steps']} (initial = {init_sep}):")
    seps = Counter(round(r['Y2_final'] - r['Y1_final'], 4) for r in all_results)
    for sep, count in sorted(seps.items()):
        marker = "  <- attracted" if sep < init_sep else \
                 "  <- repelled" if sep > init_sep else ""
        print(f"    sep = {sep:>5.2f}  ->  {count:>4d}{marker}")
    print()

    if positives:
        print(f"  Configurations with mutual_attraction > 0 ({len(positives)}):")
        header = (f"    {'alpha':>5} | {'thr':>4} | {'gamma':>5} | "
                  f"{'kappa':>5} | {'eta':>4} || "
                  f"{'Y1_fin':>8} | {'Y2_fin':>8} | "
                  f"{'defl_Y1':>9} | {'defl_Y2':>9} | {'mutual':>9}")
        print(header)
        print("    " + "-" * (len(header) - 4))
        for r in positives:
            print(f"    {r['alpha']:>5.2f} | {r['threshold']:>4.2f} | "
                  f"{r['gamma']:>5.3f} | {r['kappa']:>5.3f} | {r['eta']:>4.2f} || "
                  f"{r['Y1_final']:>8.4f} | {r['Y2_final']:>8.4f} | "
                  f"{r['defl_Y1']:>+9.4f} | {r['defl_Y2']:>+9.4f} | "
                  f"{r['mutual_attraction']:>+9.4f}")
    else:
        print("  No configuration produced positive mutual deflection.")
    print()

    long_run = data.get("long_run")
    if long_run:
        print("  LONG-RUN sanity check (same params, longer integration):")
        print(f"    params         : {long_run['params']}")
        print(f"    stable         : {long_run['stable']}")
        print(f"    steps complete : {long_run['n_steps_completed']}/"
              f"{long_run['params']['steps']}")
        print(f"    Y1_final       : {long_run['Y1_final']:+.4f}")
        print(f"    Y2_final       : {long_run['Y2_final']:+.4f}")
        print(f"    defl_Y1        : {long_run['defl_Y1']:+.4f}")
        print(f"    defl_Y2        : {long_run['defl_Y2']:+.4f}")
        print(f"    mutual_attr.   : {long_run['mutual_attraction']:+.4f}")
        if long_run["mutual_attraction"] > 0.0:
            print("    VERDICT        : attraction persists at long integration time. [OK]")
        else:
            print("    VERDICT        : attraction does NOT persist; the 80-step")
            print("                     positive deflection appears to be a transient")
            print("                     lattice fluctuation (~ quarter-cell jitter).")
    print()


def write_trajectory_csv(long_run: dict[str, Any], cy1: int, cy2: int) -> None:
    traj_y1 = long_run["trajectory_Y1"]
    traj_y2 = long_run["trajectory_Y2"]
    bits = long_run["bits_log"]
    splits = long_run["split_log"]
    n = len(traj_y1)
    with open(TABLE_PATH, "w", encoding="utf-8") as f:
        f.write("step,Y1,Y2,defl_Y1,defl_Y2,separation,mutual_attraction,"
                "total_bits,bits_glider1,bits_glider2\n")
        for t in range(n):
            y1 = traj_y1[t]
            y2 = traj_y2[t]
            d1 = y1 - cy1
            d2 = y2 - cy2
            sep = y2 - y1
            mutual = d1 - d2
            n1, n2 = splits[t] if t < len(splits) else (-1, -1)
            b = bits[t] if t < len(bits) else -1
            f.write(f"{t},{y1:.6f},{y2:.6f},{d1:+.6f},{d2:+.6f},"
                    f"{sep:+.6f},{mutual:+.6f},{b},{n1},{n2}\n")


def write_trajectory_plot(long_run: dict[str, Any], cy1: int, cy2: int,
                          best: dict[str, Any]) -> None:
    traj_y1 = long_run["trajectory_Y1"]
    traj_y2 = long_run["trajectory_Y2"]
    steps = list(range(len(traj_y1)))
    sep = [y2 - y1 for y1, y2 in zip(traj_y1, traj_y2)]
    init_sep = cy2 - cy1

    fig, (ax_pos, ax_sep) = plt.subplots(
        2, 1, figsize=(9.5, 7.0), sharex=True,
        gridspec_kw={"height_ratios": [3, 2]})
    ax_pos.plot(steps, traj_y1, "-o", color="#1f77b4", ms=3, lw=1.4,
                label="Glider 1 centroid Y1")
    ax_pos.plot(steps, traj_y2, "-s", color="#d62728", ms=3, lw=1.4,
                label="Glider 2 centroid Y2")
    ax_pos.axhline(cy1, color="#1f77b4", ls=":", lw=1.0, alpha=0.55,
                   label=f"seed cy1={cy1}")
    ax_pos.axhline(cy2, color="#d62728", ls=":", lw=1.0, alpha=0.55,
                   label=f"seed cy2={cy2}")
    ax_pos.set_ylabel("Y centroid (lattice units)")
    ax_pos.set_title(
        "Best two-body trajectory  (alpha={a}, threshold={t}, gamma={g}, "
        "kappa={k}, eta={e})".format(
            a=best["alpha"], t=best["threshold"], g=best["gamma"],
            k=best["kappa"], e=best["eta"]))
    ax_pos.legend(loc="center right", fontsize=8, framealpha=0.85)
    ax_pos.grid(True, alpha=0.3)

    ax_sep.plot(steps, sep, "-^", color="#2ca02c", ms=3, lw=1.4,
                label="separation Y2 - Y1")
    ax_sep.axhline(init_sep, color="black", ls="--", lw=0.9, alpha=0.6,
                   label=f"initial sep = {init_sep}")
    ax_sep.set_xlabel("step")
    ax_sep.set_ylabel("separation (lattice units)")
    ax_sep.legend(loc="best", fontsize=8, framealpha=0.85)
    ax_sep.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(PLOT_PATH, dpi=140)
    plt.close(fig)


def report_question3_trajectory(data: dict[str, Any],
                                best: dict[str, Any]) -> None:
    section("Q3. BEST TRAJECTORY — plot + table")
    long_run = data.get("long_run")
    if long_run is None or not long_run.get("trajectory_Y1"):
        print("  No long-run trajectory data is available; skipping.")
        return

    cy1, cy2 = data["meta"]["cy1"], data["meta"]["cy2"]
    write_trajectory_csv(long_run, cy1, cy2)
    write_trajectory_plot(long_run, cy1, cy2, best)
    print(f"  Wrote trajectory CSV : {TABLE_PATH}")
    print(f"  Wrote trajectory PNG : {PLOT_PATH}")
    print()

    traj_y1 = long_run["trajectory_Y1"]
    traj_y2 = long_run["trajectory_Y2"]
    n_pts = len(traj_y1)
    if n_pts == 0:
        return

    step_size = max(1, n_pts // 12)
    sample_steps = sorted(set(list(range(0, n_pts, step_size)) + [n_pts - 1]))
    print("  Sampled trajectory:")
    print(f"  {'step':>5} | {'Y1':>9} | {'Y2':>9} | {'sep':>6} | "
          f"{'defl_Y1':>9} | {'defl_Y2':>9} | {'mutual':>9}")
    print("  " + "-" * 78)
    for t in sample_steps:
        y1 = traj_y1[t]
        y2 = traj_y2[t]
        sep = y2 - y1
        d1 = y1 - cy1
        d2 = y2 - cy2
        print(f"  {t:>5d} | {y1:>9.4f} | {y2:>9.4f} | {sep:>6.2f} | "
              f"{d1:>+9.4f} | {d2:>+9.4f} | {d1 - d2:>+9.4f}")
    print()


def report_question4_more_sweeps(data: dict[str, Any],
                                 best: dict[str, Any]) -> None:
    section("Q4. SHOULD WE SWEEP MORE PARAMETERS?")
    grid = data["param_grid"]
    all_results = data["all_results"]

    def slice_along(varying: str) -> list[tuple[float, float]]:
        """For each value of `varying`, hold other 4 params at the best config
        and return (value, mutual_attraction)."""
        out: list[tuple[float, float]] = []
        for v in grid[varying]:
            for r in all_results:
                if r[varying] != v:
                    continue
                if all(r[k] == best[k] for k in
                       ("alpha", "threshold", "gamma", "kappa", "eta")
                       if k != varying):
                    out.append((v, r["mutual_attraction"]))
                    break
        return out

    print(f"  Holding other params at best config and varying one at a time:")
    print(f"  best = alpha={best['alpha']} threshold={best['threshold']} "
          f"gamma={best['gamma']} kappa={best['kappa']} eta={best['eta']}")
    print()

    advice: list[str] = []
    for name in ("alpha", "threshold", "gamma", "kappa", "eta"):
        sweep_vals = grid[name]
        slice_ = slice_along(name)
        best_v = best[name]
        idx_best = sweep_vals.index(best_v)
        print(f"  {name}:")
        for v, m in slice_:
            mark = "  *" if v == best_v else "   "
            print(f"    {name}={v:<6}  mutual_attraction={m:+.4f}{mark}")

        # boundary detection
        is_low_boundary = idx_best == 0
        is_high_boundary = idx_best == len(sweep_vals) - 1
        # non-monotonic detection (peak isolated in interior)
        mutuals = [m for _, m in slice_]
        peak_val = max(mutuals)
        peak_count = mutuals.count(peak_val)
        flat = (peak_count == len(mutuals))

        if flat:
            advice.append(f"  - {name}: completely flat at the optimum -> no "
                          f"information; widening this axis would be wasteful.")
        elif is_low_boundary:
            advice.append(f"  - {name}: optimum sits on the LOW boundary "
                          f"({best_v}); extend the sweep DOWN below "
                          f"{sweep_vals[0]}.")
        elif is_high_boundary:
            advice.append(f"  - {name}: optimum sits on the HIGH boundary "
                          f"({best_v}); extend the sweep UP above "
                          f"{sweep_vals[-1]}.")
        else:
            # interior peak — check if neighbours also achieve peak
            neighbours_peak = (
                (idx_best > 0 and mutuals[idx_best - 1] == peak_val) or
                (idx_best < len(mutuals) - 1 and mutuals[idx_best + 1] == peak_val))
            if not neighbours_peak:
                advice.append(f"  - {name}: optimum is a SHARP interior peak "
                              f"at {best_v}; refine the grid between "
                              f"{sweep_vals[idx_best-1]} and "
                              f"{sweep_vals[idx_best+1]}.")
            else:
                advice.append(f"  - {name}: optimum sits on a plateau around "
                              f"{best_v}; the current resolution is adequate.")
        print()

    section("RECOMMENDATIONS — additional sweeps to consider")
    for line in advice:
        print(line)

    # Additional structural recommendations
    long_run = data.get("long_run")
    if long_run and long_run.get("mutual_attraction", 0.0) <= 0.0:
        print()
        print("  - The 80-step 'attraction' (mutual=+0.5) collapses to 0 at "
              f"{long_run['params']['steps']} steps -> sweep LONGER "
              "integration times (e.g. 240, 480, 960 steps) to test whether "
              "the deflection grows monotonically or is just lattice jitter.")
        print("  - All wins were quarter/half-cell discretised. Try smaller "
              "initial separation (e.g. cy2-cy1 = 4 or 5) to amplify the "
              "expected 1/r^2 force above the discretisation noise floor.")
        print("  - Consider averaging over multiple lut_seeds / sub_seeds "
              "so that the apparent attraction is not lut-specific.")
        print("  - cutoff_radius was fixed at 4. Sweep it together with "
              "alpha/eta — the effective coupling range may need to span "
              "more of the inter-particle distance ({} cells).".format(
                  data['meta']['cy2'] - data['meta']['cy1']))


def write_text_report(data: dict[str, Any], best: dict[str, Any]) -> None:
    """Tee the analysis into a plain-text artifact for the archive."""
    # Re-run the print functions with stdout redirected.
    import io
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        report_overview(data)
        report_question1_best(data, best)
        report_question2_attraction(data)
        report_question3_trajectory(data, best)
        report_question4_more_sweeps(data, best)
    finally:
        sys.stdout = old
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(buf.getvalue())


def main() -> int:
    if not os.path.exists(JSON_PATH):
        print(f"ERROR: missing input file: {JSON_PATH}", file=sys.stderr)
        return 1

    data = load_results()
    all_results = data["all_results"]
    best = find_best(all_results)

    # 1-4: print to stdout
    report_overview(data)
    report_question1_best(data, best)
    report_question2_attraction(data)
    report_question3_trajectory(data, best)
    report_question4_more_sweeps(data, best)

    # And save the same text to disk for archival.
    write_text_report(data, best)
    print()
    print(f"Saved text report to {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
