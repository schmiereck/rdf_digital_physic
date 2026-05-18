**Objective: Diagnose the persistent `ModuleNotFoundError` for the `automata-lib` package.**

**Context:**
Planner `213.5` successfully installed `automata-lib==9.2.0` via pip, but the verification step still failed with `ModuleNotFoundError`. This is the final blocker. Your task is to perform a deep-dive diagnosis of the Python environment to understand why this is happening.

**Methodology: Orchestrated Environment Inspection**

You will launch a sequence of sub-agents to act as a system administrator and debug the environment.

1.  **Sub-task 1 (Verbose Install & Inspection):**
    *   Launch an agent to run `pip install --force-reinstall automata-lib==9.2.0` to ensure a clean installation.
    *   Immediately after, run `pip show automata-lib` and `pip show -f automata-lib`. Capture the `Location:` and the list of installed files from the output. This tells you *where* the package is and *what* it contains.
2.  **Sub-task 2 (Python Path Inspection):**
    *   Launch an agent to execute a simple Python script: `import sys; import os; print(f\"sys.path: {sys.path}\"); print(f\"PYTHONPATH: {os.environ.get('PYTHONPATH')}\")`. This tells you *where Python is looking* for modules.
3.  **Sub-task 3 (Synthesize and Conclude):**
    *   Compare the installation location from Sub-task 1 with the search paths from Sub-task 2.
    *   Analyze the list of files from Sub-task 1. Does `automata-lib` contain an `__init__.py` file in its top-level directory, making it an importable module?
    *   Based on this evidence, your final report must provide a definitive explanation for the `ModuleNotFoundError`.

**Success Criterion:**
The planner must produce a clear, evidence-based conclusion that explains the import failure. For example: "The package installs to a directory not on `sys.path`," or "The package is a namespace package without a standard module structure." This conclusion will guide the final repair attempt.
