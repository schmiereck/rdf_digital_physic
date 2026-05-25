# Iter 248: Glider Verification Report
## Methodology
- **Test 1**: Single-bit decomposition. If each bit moves with the same velocity solo as in the composite, the species is a non-interacting composite.
- **Test 2**: Collision interaction. Count cells containing >1 bit across 32 steps. Zero means bits never interact.
- **Test 3**: Bit-removal stability. Removing any bit should destabilize the pattern (change velocity, break bit conservation, or expand beyond extent 6).
## Results
- Species tested: **10**
- Non-interacting composites: **10**
- Genuine gliders: **0**
- LUT-08 positive control passes all tests: **False**
## Per-Species Details
| ID | LUT | T1 (all solo match) | T2 (multi-bit cells) | T3 (removal destabilizes) | Verdict |
|---|---|---|---|---|---|
| 0 | sym_42 | True | 0 | False | NON_INTERACTING_COMPOSITE |
| 1 | sym_123 | True | 0 | False | NON_INTERACTING_COMPOSITE |
| 2 | lut08 | True | 0 | False | NON_INTERACTING_COMPOSITE |
| 3 | sym_42 | True | 0 | False | NON_INTERACTING_COMPOSITE |
| 4 | sym_123 | True | 0 | False | NON_INTERACTING_COMPOSITE |
| 5 | sym_999 | True | 0 | False | NON_INTERACTING_COMPOSITE |
| 6 | lut08 | True | 0 | False | NON_INTERACTING_COMPOSITE |
| 7 | sym_42 | True | 0 | False | NON_INTERACTING_COMPOSITE |
| 8 | sym_123 | True | 0 | False | NON_INTERACTING_COMPOSITE |
| 9 | sym_999 | True | 0 | False | NON_INTERACTING_COMPOSITE |

## Conclusion
**All 10 claimed 'novel species' are NON-INTERACTING COMPOSITES.** None exhibit coherent bit interaction required for a genuine glider.

**WARNING**: The LUT-08 reference glider failed the positive control. The test suite may be defective.
