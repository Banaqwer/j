from pathlib import Path

from vibration.utils.hashing import sha256_file


def write_predictions_with_header(path: str) -> dict[str, str]:
    checksum = sha256_file(path)
    return {"version": "0.1.0", "sha256": checksum, "path": str(Path(path))}
