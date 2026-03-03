from vibration.qc.qc_schema import REQUIRED_HEADER_FIELDS


def test_qc_header_fields() -> None:
    assert set(REQUIRED_HEADER_FIELDS) == {"version", "sha256"}
