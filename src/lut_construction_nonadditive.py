import numpy as np
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.search_3d_gliders import (
    get_oh_permutations, precompute_perm_action, compute_orbits, compute_all_stabilizers, verify_lut
)

def build_modified_lut(base_lut, action, mods):
    """
    mods: dict mapping representative state to target state.
    For each (rep, target), we find all g in O_h and map g(rep) -> g(target).
    """
    lut = base_lut.copy()
    n_perms = action.shape[0]
    for rep, target in mods.items():
        # Get all O_h transformations of the representative and target
        for g in range(n_perms):
            s = int(action[g, rep])
            d = int(action[g, target])
            lut[s] = d
    return lut

def main():
    # Load LUT-08
    with open(ROOT / "archive/iter_224/results/glider_00_lut08_sub03.json") as f:
        ref = json.load(f)
    lut08 = np.array(ref["lut"], dtype=np.uint16)

    perms = get_oh_permutations()
    action = precompute_perm_action(perms)

    # 1. LUT-INT-EXCHANGE
    # Map O_2 to swap-cycles (34 = ch[1,5]), O_3 to swap-cycles (40 = ch[3,5])
    # O_0 remains default (12 = ch[2,3])
    exchange_mods = {17: 34, 20: 40}
    lut_exchange = build_modified_lut(lut08, action, exchange_mods)
    
    # 2. LUT-INT-BINDING
    # Map O_2 to identity (17 = ch[0,4]), O_3 to identity (20 = ch[2,4])
    # O_0 maps to identity (3 = ch[0,1])
    binding_mods = {17: 17, 20: 20, 3: 3}
    lut_binding = build_modified_lut(lut08, action, binding_mods)

    # 3. LUT-INT-SCATTERING
    # Map O_2 to other swap-cycles (68 = ch[2,6]), O_3 to default (65 = ch[0,6])
    # O_0 maps to swap-cycles (48 = ch[4,5])
    scattering_mods = {17: 68, 20: 65, 3: 48}
    lut_scattering = build_modified_lut(lut08, action, scattering_mods)

    # Verify all LUTs
    luts = {
        "exchange": lut_exchange,
        "binding": lut_binding,
        "scattering": lut_scattering
    }

    for name, lut in luts.items():
        v = verify_lut(lut, action)
        print(f"[{name}] Verification:")
        print(f"  Bijection: {v['bijection']}")
        print(f"  Bit conserving: {v['bit_conserving']}")
        print(f"  O_h symmetric: {v['symmetric']}")
        assert v['bijection'] and v['bit_conserving'] and v['symmetric'], f"{name} verification failed!"

    # Save to src/
    np.save(ROOT / "src/nonadditive_lut_exchange.npy", lut_exchange)
    np.save(ROOT / "src/nonadditive_lut_binding.npy", lut_binding)
    np.save(ROOT / "src/nonadditive_lut_scattering.npy", lut_scattering)
    print("All LUT variants saved successfully!")

if __name__ == "__main__":
    main()
