#!/usr/bin/env python3
"""Pair Production Experiment (iter_247)"""
import json, sys
from pathlib import Path
from collections import deque
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.engine_3d import stream, collide
from src.glider_charge_analysis import make_BT, reflect
from src.rigorous_glider_audit import build_oh_transforms, seed_grid, compute_com_circular, grid_cells, is_translate
L = 64

def load():
    with open(ROOT / "archive/iter_224/results/glider_00_lut08_sub03.json") as f:
        d = json.load(f)
    return np.array(d["lut"], np.uint16), [tuple(c) for c in d["particle"]]

def step(g, lut): return collide(stream(g), lut)

def disp1(part, lut):
    g = seed_grid(L, part); g1 = step(g, lut)
    c0, _ = compute_com_circular(g); c1, _ = compute_com_circular(g1)
    return np.array([(c1[i]-c0[i]+L/2)%L-L/2 for i in range(3)])

def find_pC(pA, lut, transforms):
    dA = disp1(pA, lut); best = None; bestsc = -1
    for perm, M in transforms:
        if round(np.linalg.det(M)) != 1: continue
        pC = [(int(round(v[0])), int(round(v[1])), int(round(v[2])), int(perm[ch])) for l,r,c,ch in pA for v in [M @ np.array([l,r,c], float)]]
        dC = disp1(pC, lut); sc = -np.linalg.norm(dC+dA)
        if best is None or sc > bestsc: best, bestsc = pC, sc
    return best

def solo(part, lut, steps=80):
    g = seed_grid(L, part)
    for _ in range(steps):
        g = step(g, lut)
        if int(g.sum()) != len(part): return False
    return True

def tdist(a, b, L): return sum(min(abs(a[i]-b[i]), L-abs(a[i]-b[i])) for i in range(3))

def cluster_cells(cells, R=4):
    pos = [(c[0], c[1], c[2]) for c in cells]; n = len(pos); seen = [False]*n; out = []
    for i in range(n):
        if seen[i]: continue
        comp, seen[i], q = [i], True, deque([i])
        while q:
            u = q.popleft()
            for j in range(n):
                if seen[j]: continue
                if tdist(pos[u], pos[j], L) <= R: seen[j] = True; comp.append(j); q.append(j)
        out.append([cells[k] for k in comp])
    return out

def run_collision(pA, pC, oa, ob, lut, steps=300, save_every=10):
    g = np.zeros((L, L, L, 12), np.uint8)
    for dl, dr, dc, ch in pA: g[(oa[0]+dl)%L, (oa[1]+dr)%L, (oa[2]+dc)%L, ch] = 1
    for dl, dr, dc, ch in pC: g[(ob[0]+dl)%L, (ob[1]+dr)%L, (ob[2]+dc)%L, ch] = 1
    saved = {}
    for t in range(steps+1):
        if t % save_every == 0: saved[t] = grid_cells(g)
        g = step(g, lut)
    return saved

def com_of_cells(cells):
    g = np.zeros((L, L, L, 12), np.uint8)
    for l, r, c, ch in cells: g[l, r, c, ch] = 1
    return compute_com_circular(g)[0]

def track_clusters(saved):
    asteps = sorted(s for s in saved if s >= 60); tracks, next_id, prev = [], 0, {}
    for t in asteps:
        clusters = cluster_cells(list(saved[t])); curr, matched = {}, set(); cands = []
        for cl in clusters:
            ps = frozenset((c[0], c[1], c[2]) for c in cl)
            best_pid, best_ov = None, -1
            for pid, pcl in prev.items():
                if pid in matched: continue
                ov = len(ps & frozenset((c[0], c[1], c[2]) for c in pcl))
                if ov > best_ov: best_ov, best_pid = ov, pid
            cands.append((cl, best_pid, best_ov))
        for cl, best_pid, best_ov in cands:
            if best_pid is not None and best_pid not in matched and best_ov > 0: cid = best_pid; matched.add(cid)
            else: cid = next_id; next_id += 1
            curr[cid] = cl; found = False
            for tr in tracks:
                if tr["id"] == cid: tr["steps"].append((t, cl, com_of_cells(cl), len(cl))); found = True; break
            if not found: tracks.append({"id": cid, "steps": [(t, cl, com_of_cells(cl), len(cl))]})
        prev = curr
    return tracks

def classify_track(tr, L):
    if len(tr["steps"]) < 2: return "transient", None, None, None, None
    coms = [s[2] for s in tr["steps"]]; dvec = np.zeros(3)
    for i in range(1, len(coms)):
        diff = coms[i]-coms[i-1]
        for a in range(3):
            if diff[a] > L/2: diff[a] -= L
            elif diff[a] < -L/2: diff[a] += L
        dvec += diff
    disp = np.linalg.norm(dvec); dt = tr["steps"][-1][0]-tr["steps"][0][0]
    vvec = dvec/dt if dt > 0 else np.zeros(3); v = np.linalg.norm(vvec); vs = []
    for i in range(1, len(coms)):
        diff = coms[i]-coms[i-1]
        for a in range(3):
            if diff[a] > L/2: diff[a] -= L
            elif diff[a] < -L/2: diff[a] += L
        vs.append(np.linalg.norm(diff)/(tr["steps"][i][0]-tr["steps"][i-1][0]))
    v_mean = np.mean(vs) if vs else 0; v_var = (np.std(vs)/v_mean if v_mean > 0 else 0)
    shapes = [frozenset(c for c in s[1]) for s in tr["steps"]]; period = None
    for p in range(1, len(shapes)):
        ok = True
        for i in range(len(shapes)-p):
            if not is_translate(shapes[i], shapes[i+p], L): ok = False; break
        if ok: period = p; break
    if disp >= 2 and v_var < 0.20: return "propagating", v, vvec, period, v_var
    if disp < 1: return "stationary", v, vvec, period, v_var
    return "transient", v, vvec, period, v_var

def vacuum_isolation(cells, lut):
    pos = np.array([(c[0], c[1], c[2]) for c in cells]); mn = pos.min(axis=0)
    part = [(int(c[0]-mn[0]), int(c[1]-mn[1]), int(c[2]-mn[2]), int(c[3])) for c in cells]
    g = seed_grid(L, part, center=(32,32,32)); bits = int(g.sum()); coms = [compute_com_circular(g)[0]]; shapes = [grid_cells(g)]
    for _ in range(300):
        g = step(g, lut)
        if int(g.sum()) != bits: return False, "bit_count_changed", None
        coms.append(compute_com_circular(g)[0]); shapes.append(grid_cells(g))
    vs = []
    for i in range(1, len(coms)):
        diff = coms[i]-coms[i-1]
        for a in range(3):
            if diff[a] > L/2: diff[a] -= L
            elif diff[a] < -L/2: diff[a] += L
        vs.append(np.linalg.norm(diff))
    v_mean = np.mean(vs)
    if v_mean > 0 and np.std(vs)/v_mean > 0.10: return False, "velocity_drift", v_mean
    period = None
    for p in range(1, min(21, len(shapes))):
        ok = True
        for i in range(len(shapes)-p):
            if not is_translate(shapes[i], shapes[i+p], L): ok = False; break
        if ok: period = p; break
    if period is None: return False, "no_periodicity", v_mean
    return True, "stable", v_mean

def main():
    lut, pA = load(); transforms = build_oh_transforms()
    pC = find_pC(pA, lut, transforms)
    print("pC found, solo stable:", solo(pC, lut, 80))
    g = seed_grid(L, pA); coms = [compute_com_circular(g)[0]]
    for _ in range(80): g = step(g, lut); coms.append(compute_com_circular(g)[0])
    d = np.zeros(3)
    for i in range(1, len(coms)):
        diff = coms[i]-coms[i-1]
        for a in range(3):
            if diff[a] > L/2: diff[a] -= L
            elif diff[a] < -L/2: diff[a] += L
        d += diff
    v_lut = d/80; print(f"LUT-08 velocity: {v_lut}")
    oh_vels = [M @ v_lut for perm, M in transforms]
    g = seed_grid(L, pA); vac_ok = True
    for t in range(300):
        g = step(g, lut)
        if int(g.sum()) != 4: vac_ok = False; break
        if t % 10 == 0:
            cs = cluster_cells(list(grid_cells(g)))
            if len(cs) != 1 or len(cs[0]) != 4: vac_ok = False; break
    print(f"Vacuum control: {vac_ok}")
    dys = [0, 1, -1, 2, -2, 3, -3, 4, -4]; baseA, baseC = (20, 32, 20), (44, 32, 44)
    all_results, new_candidates = [], []
    for dy in dys:
        oa, ob = baseA, (baseC[0]%L, (baseC[1]+dy)%L, baseC[2]%L)
        saved = run_collision(pA, pC, oa, ob, lut, 300, 10)
        tracks = track_clusters(saved); config_result = {"dy": dy, "tracks": []}
        for tr in tracks:
            kind, v, vvec, period, vvar = classify_track(tr, L)
            bc = tr["steps"][0][3] if tr["steps"] else 0
            info = {"id": tr["id"], "kind": kind, "bits": bc, "velocity": float(v) if v is not None else None, "period": period, "v_var": float(vvar) if vvar is not None else None}
            if kind == "propagating":
                is_lut08 = False
                if bc == 4 and period is not None and abs(period-2) <= 1:
                    for ov in oh_vels:
                        if np.linalg.norm(vvec-ov) < 0.3: is_lut08 = True; break
                if is_lut08: info["classification"] = "LUT-08_scattered"
                else:
                    info["classification"] = "NEW_CANDIDATE"
                    stable, reason, v_iso = vacuum_isolation(tr["steps"][0][1], lut)
                    info["vacuum_test"] = {"stable": stable, "reason": reason, "v_iso": float(v_iso) if v_iso else None}
                    if stable: new_candidates.append(info)
            else: info["classification"] = kind
            config_result["tracks"].append(info)
        all_results.append(config_result)
        n_new = sum(1 for t in config_result["tracks"] if t.get("classification") == "NEW_CANDIDATE")
        n_prop = sum(1 for t in config_result["tracks"] if t["kind"] == "propagating")
        print(f"dy={dy:3d}: propagating={n_prop}, new_candidates={n_new}")
    total_prop = sum(1 for c in all_results for t in c["tracks"] if t["kind"] == "propagating")
    total_new = len(new_candidates); total_stat = sum(1 for c in all_results for t in c["tracks"] if t["kind"] == "stationary")
    f1 = total_prop == 0
    f2 = total_prop > 0 and total_new == 0 and all(t.get("classification") == "LUT-08_scattered" for c in all_results for t in c["tracks"] if t["kind"] == "propagating")
    f3 = total_prop == 0 and total_stat > 0
    new_dys = set()
    for c in all_results:
        for t in c["tracks"]:
            if t.get("classification") == "NEW_CANDIDATE": new_dys.add(c["dy"])
    robust = False
    for dy in new_dys:
        if (dy+1) in new_dys or (dy-1) in new_dys: robust = True; break
    f4 = len(new_dys) > 0 and not robust
    verdict = "REFUTED" if (f1 or f2 or f3 or f4) else "SUPPORTED"
    print(f"\nF1={f1} F2={f2} F3={f3} F4={f4}"); print(f"Verdict: {verdict}")
    out = {"lut08_velocity": v_lut.tolist(), "vacuum_control": vac_ok, "configs": all_results, "new_candidates": new_candidates, "falsification": {"F1": f1, "F2": f2, "F3": f3, "F4": f4}, "verdict": verdict}
    outd = ROOT / "archive/iter_247/results"; outd.mkdir(parents=True, exist_ok=True)
    with open(outd / "pair_production_results.json", "w") as f: json.dump(out, f, indent=2)
    print(f"Saved to {outd / 'pair_production_results.json'}")

if __name__ == "__main__": main()
