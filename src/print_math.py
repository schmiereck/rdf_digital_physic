#!/usr/bin/env python3
"""Print the exact lines of DisplacementConsistencyFitness.__call__ from
src/new_fitness.py, lines 220 through 350 inclusive."""

import os
import sys

WORK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_FILE = os.path.join(WORK_DIR, "src", "new_fitness.py")

start_line = 220
end_line = 350

with open(TARGET_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Ensure stdout can output UTF-8 even on Windows
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

for i in range(start_line - 1, min(end_line, len(lines))):
    print(lines[i], end="")
