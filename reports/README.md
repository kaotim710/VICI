# Generated Reports

This directory is the default output location for local evaluation and review scripts.

Most report files are generated artifacts and are intentionally ignored by git. Re-run the relevant script to refresh them locally:

```bash
python3 scripts/evaluate_seed.py
python3 scripts/evaluate_validation.py
python3 scripts/evaluate_regression.py
python3 scripts/evaluate_gold_boundaries.py
python3 scripts/export_seed_extractions_md.py
python3 scripts/export_warning_audit_md.py
python3 scripts/run_recovery_actions.py
```

`live_sec_smoke_summary.json` is kept as a small frontend testing sample for the `/testing` page.
