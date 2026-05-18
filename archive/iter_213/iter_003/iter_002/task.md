# Task: Install automata-lib and Re-test Import

This is a two-step task.

**Step 1: Install the library**

1.  Execute the following command to install the `automata-lib` package using pip from the project's virtual environment:
    `.venv/Scripts/python.exe -m pip install automata-lib`
2.  Capture the output. If the installation is successful, proceed to Step 2. If it fails, stop and report the error.

**Step 2: Re-run the import test**

1.  Execute the *exact same script* from the previous step: `src/test_import.py`. The command is:
    `.venv/Scripts/python.exe src/test_import.py`
2.  Capture all stdout and stderr from this execution.
3.  Report the outcome of both steps.

The final status should be `ok` if and only if both the installation and the subsequent import test are successful.

```yaml
status: ok
artifacts: []
metrics: {}
log_excerpt: |
  ...
experimenter_view: |
  ...
notes: "Attempting to install automata-lib and re-run import test."
```