Fix and run the 3D FCC embedding test files.

The files src/fcc_engine_embed.py and src/test_embedded_glider.py were written by a previous agent but:
1. Have import path issues (`from src.xxx import yyy` won't work — should be `from xxx import yyy` with sys.path setup)
2. Were never executed (encoding error prevented running)

TASK:
1. Fix src/fcc_engine_embed.py: change `from src.fcc_engine_13ch import SHIFTS_13` to use sys.path insert pattern like other files in the project. Look at src/experiment_250_hex_decomposition.py for the correct pattern:
```python
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from fcc_engine_13ch import SHIFTS_13
```

2. Fix src/test_embedded_glider.py: same import fix pattern. Also:
   - Replace `from src.evolution import ...` with proper sys.path import
   - Replace `from src.fcc_engine_embed import ...` with proper sys.path import
   - Make sure CHAMPION_PATH uses PROJECT_ROOT variable
   - Make sure OUTPUT_DIR uses PROJECT_ROOT variable
   - Remove any unicode characters (alpha symbol etc.) that caused encoding issues — use ASCII only

3. Run src/test_embedded_glider.py and save results to archive/iter_252/results/

4. After running, read the output files (embed_test.json and embed_report.json) and report the key findings:
   - Is F3 triggered?
   - Does the embedded glider survive?
   - Does the decomposition test pass?
   - Does the positive control match?

Keep the files clean, under 200 lines each, ASCII only.