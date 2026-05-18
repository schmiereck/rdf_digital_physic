# Task: Basic Library Import Test

1.  Create a new Python script at `src/test_import.py`.
2.  The script should contain only the following code:
    ```python
    import sys
    try:
        print("Attempting to import from automata_lib.ca...")
        from automata_lib import ca
        print("Import successful.")
        sys.exit(0)
    except ImportError as e:
        print(f"ImportError: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during import: {e}", file=sys.stderr)
        sys.exit(1)
    ```
3.  Execute the script `src/test_import.py` using `python3`.
4.  Capture all stdout and stderr.
5.  Report back with the result. If the script prints "Import successful." and exits with code 0, the status is 'ok'. Otherwise, the status is 'experiment_failed'.

Your final YAML response must include the full output of the script.
```yaml
status: ok
artifacts:
  - src/test_import.py
metrics: {}
log_excerpt: |
  ...
experimenter_view: |
  ...
notes: "Basic import test."
```