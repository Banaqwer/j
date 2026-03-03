# AGENTS

## Scope
These instructions apply to the entire `vibration_qc_max/` tree.

## Engineering rules
- Keep implementation deterministic with explicit seeds for Python, NumPy, and Torch.
- Maintain leak-free temporal logic in all train/test and feature/label code.
- Keep QuantConnect integration parity-safe: QC consumes exported predictions, no local model/ephemeris in QC runtime.
- Preserve strict typing where practical; keep ruff and mypy clean.
