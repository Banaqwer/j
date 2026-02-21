# SPEC_COMPLIANCE

## Phase 0
- SPEC sections: C1 (timezone/config scaffold), C3/C7 (circular math + kappa primitive), C9 (bisection primitive scaffold), C18 (QC ObjectStore key schema scaffold), and Section E CLI command surface.
- Implemented files:
  - `vibration/cli.py`
  - `vibration/config/spy_daily.yaml`
  - `vibration/utils/seed.py`
  - `vibration/ephemeris/geometry.py`
  - `vibration/ephemeris/moon_events.py`
  - `vibration/features/{fft_locked.py,dtw_locked.py,wavelet_locked.py}`
  - `vibration/models/{preprocess_foldsafe.py,stacking_timeseries.py}`
  - `vibration/backtest/execution_rules.py`
  - `vibration/stats/placebos.py`
  - `vibration/qc/{qc_schema.py,export_to_qc.py}`
  - CI/tooling: `.github/workflows/ci.yml`, `pyproject.toml`, `mypy.ini`, `requirements.txt`, `requirements.lock`
- Tests/checks:
  - `pytest -q` (13 passed)
  - `ruff check .` (all checks passed)
  - `mypy vibration` (success)
- Artifact outputs:
  - No research artifacts in phase 0 (scaffold only).
