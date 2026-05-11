# Task – iter_102

**Hypothesis:** [mock] lr-2e4: doubling LR to 2e-4 with warmup achieves val_loss < 3.0

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_102/results/` (relative to the project root).

## Task

Create archive/iter_103/code/run.py that prints 'hello from iter 103' and exits 0.

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
