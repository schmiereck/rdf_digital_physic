# Task – iter_106

**Hypothesis:** [mock] lr-2e4: doubling LR to 2e-4 with warmup achieves val_loss < 3.0

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch.
Write results and data files to `archive/iter_106/results/` (relative to the project root).

## Task

Create src/run_iter_107.py that prints 'hello from iter 107' and exits 0.

## Success Criteria

- Script exits with code 0
- result.yaml present

## Required Output

You MUST end your final response with a ```yaml``` code block in this exact schema (the orchestrator reads it to determine success):

```yaml
status: ok  # or experiment_failed or code_error
artifacts:
  - path/to/created/file  # relative to the project root
metrics:
  key: value  # any numeric results
log_excerpt: |  # last ~20 lines of relevant output
  ...
experimenter_view: |  # your qualitative observations
  ...
notes: brief technical remark
```
