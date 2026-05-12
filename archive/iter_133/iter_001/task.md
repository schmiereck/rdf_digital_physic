
Create a Python script `src/characterize_remnant.py` to analyze the composition of the stable remnant produced by `iter_131/population/rule_011.json`.

**1. Generate the Remnant:**
- Load the canonical ash pattern from `src/ash_pattern.json`.
- Load the rule from `archive/iter_131/population/rule_011.json`.
- Run the simulation for 200 steps on a 200x200 grid with wrapping boundaries to generate the stable remnant.

**2. Isolate and Characterize Objects:**
- Use a connected-components algorithm on the grid state at step 200 to get a list of all distinct objects.
- For each object:
    a. Create a small, isolated simulation containing only that object's cells.
    b. Simulate this isolated object for up to 100 steps to determine its period. The period is found when the (translation-normalized) set of live cells repeats.
    c. If the object is a still-life, its period is 1. If it vanishes, record it as decayed.
    d. Store the period and the sequence of (translation-normalized) shapes for each unique phase of the oscillation.

**3. Catalog Unique Oscillator Types:**
- Group the characterized objects by their period and normalized shape sequences. Two objects belong to the same type if these characteristics match.
- Count the number of unique types found.

**4. Report Results:**
- Create the main results file `archive/iter_133/result.yaml` with the following keys:
    - `total_objects_in_remnant`: The total number of connected components found.
    - `unique_oscillator_types_count`: The number of unique oscillator types discovered.
    - `still_life_count`: The number of objects with period 1.
    - `decayed_count`: The number of objects that vanished when isolated.
    - `type_counts`: A dictionary mapping a unique type ID (e.g., "p2_blinker_6bit") to its count in the remnant.
- For each unique oscillator type found, create a detailed JSON file in `archive/iter_133/results/`. The filename should reflect the type (e.g., `p2_blinker_6bit.json`). This file should contain:
    - `period`: The period of the oscillator.
    - `bit_count`: The number of live cells.
    - `phases`: A list of the shapes for each phase, where each shape is a list of relative cell coordinates `[q, r]`.
