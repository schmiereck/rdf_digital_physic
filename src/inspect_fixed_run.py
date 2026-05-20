#!/usr/bin/env python3
"""
inspect_fixed_run.py

Reads src/run_evolution_exp_220_fixed.py, extracts and prints:
  - chromosome_to_rule_dict
  - rule_dict_to_chromosome
  - main
  - any other conversion helpers

Prints each function with annotations explaining the mapping logic.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_PATH = PROJECT_ROOT / "src" / "run_evolution_exp_220_fixed.py"


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_top_level_definitions(source: str) -> dict[str, str]:
    """
    Track indentation to find function boundaries.
    Returns {name: source_text} for all top-level functions and classes.
    """
    definitions: dict[str, str] = {}
    lines = source.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        # Match top-level def or class (no leading whitespace)
        if not line.startswith(" ") and not line.startswith("\t") and \
           re.match(r"^(def|class)\s+(\w+)\s*", stripped):
            match = re.match(r"^(def|class)\s+(\w+)", stripped)
            name = match.group(2)
            def_indent = len(line) - len(line.lstrip())  # should be 0
            # The body is indented more than the def line
            block_lines = [line]
            i += 1
            while i < len(lines):
                cur = lines[i]
                if cur.strip() == "":
                    block_lines.append(cur)
                    i += 1
                    continue
                cur_indent = len(cur) - len(cur.lstrip())
                if cur_indent > def_indent:
                    block_lines.append(cur)
                    i += 1
                else:
                    break
            definitions[name] = "".join(block_lines)
        else:
            i += 1
    return definitions


def annotate_mapping(func_name: str, func_source: str) -> str:
    """
    Add human-readable annotation about what the function does
    and how it maps data.
    """
    annotations = {
        "chromosome_to_rule_dict": """
    +----------------------------------------------------------+
    |  MAPPING: chromosome (1-bit array)  ->  rule_dict        |
    +==========================================================+
    |  A chromosome is a 128-element uint8 array (0 or 1).     |
    |  Each index s (0..127) represents a 3-bit neighborhood   |
    |  configuration in a 2D cellular automaton.               |
    |                                                          |
    |  The rule for state s is encoded as:  value = (out<<6)   |
    |    | center_bit | neighbor_bits[5]..[0]                  |
    |  where:                                                  |
    |    center_bit = (s >> 6) & 1    <- "default" center      |
    |    actual_center = chrom[s]    <- evolved bit            |
    |                                                          |
    |  This function only stores entries where actual_center   |
    |  != default_center (the rest are implicit / default).    |
    |                                                          |
    |  OUTPUT: dict mapping { neighborhood_index : encoded }   |
    +----------------------------------------------------------+
""",
        "rule_dict_to_chromosome": """
    +----------------------------------------------------------+
    |  MAPPING: rule_dict  ->  chromosome (1-bit array)        |
    +==========================================================+
    |  Reverse of chromosome_to_rule_dict.                     |
    |                                                          |
    |  For each (k, v) in rule_dict:                           |
    |    lut[k] = v                                            |
    |                                                          |
    |  Then for every lut entry:                               |
    |    chromosome[k] = (lut[k] >> 6) & 1                     |
    |    <- extract just the center bit                        |
    |                                                          |
    |  OUTPUT: numpy uint8 array of length 128                 |
    +----------------------------------------------------------+
""",
        "rule_dict_to_lut": """
    +----------------------------------------------------------+
    |  MAPPING: rule_dict  ->  LUT (full lookup table)         |
    +==========================================================+
    |  Converts the sparse rule_dict back into a full          |
    |  128-entry lookup table where missing entries get        |
    |  their "default" value: default = (index >> 6) & 1      |
    |                                                          |
    |  OUTPUT: numpy uint8 array of length 128 (full LUT)      |
    +----------------------------------------------------------+
""",
        "main": """
    +----------------------------------------------------------+
    |  MAIN EVOLUTION LOOP                                     |
    +==========================================================+
    |  Workflow:                                               |
    |                                                          |
    |  1. Generate initial population (random C2 rules)        |
    |     -> rule_dict  ->  rule_dict_to_chromosome()          |
    |     -> population: list[np.ndarray]                      |
    |                                                          |
    |  2. For each generation:                                 |
    |     a. evaluate_population:                              |
    |        -> chromosome_to_rule_dict(chrom)                 |
    |        -> evaluate_rule() -> simulate_with_history()     |
    |        -> DisplacementConsistencyFitness score           |
    |                                                          |
    |     b. select_top_k (elitism)                            |
    |     c. swap_mutate children from elites                  |
    |                                                          |
    |  3. Save champion:                                       |
    |     -> chromosome_to_rule_dict(champion_chrom)           |
    |     -> JSON: {rule_dict, chromosome, fitness, ...}       |
    +----------------------------------------------------------+
""",
    }
    return annotations.get(func_name, "")


def main():
    print("=" * 70)
    print("  Inspecting: run_evolution_exp_220_fixed.py")
    print(f"  Source file: {SOURCE_PATH}")
    print("=" * 70)
    print()

    source = read_source(SOURCE_PATH)
    definitions = extract_top_level_definitions(source)

    # Print total count
    print(f"  Found {len(definitions)} top-level definitions")
    print()

    # Priority functions to print first
    target_names = [
        "chromosome_to_rule_dict",
        "rule_dict_to_chromosome",
        "rule_dict_to_lut",
        "main",
    ]

    # Add any remaining functions
    for name in definitions:
        if name not in target_names:
            target_names.append(name)

    # Print each definition
    for func_name in target_names:
        if func_name not in definitions:
            print(f"  [!] {func_name}: NOT FOUND in source")
            print()
            continue

        source_text = definitions[func_name]
        annotation = annotate_mapping(func_name, source_text)

        print("-" * 70)
        print(f"  FUNCTION: {func_name}")
        print(annotation)
        print("-" * 70)
        print("  >>> SOURCE CODE <<<")
        print("-" * 70)
        print(source_text.rstrip())
        print()

    print("=" * 70)
    print("  Inspection complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()
