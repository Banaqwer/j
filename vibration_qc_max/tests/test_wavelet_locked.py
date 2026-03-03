from vibration.features.wavelet_locked import normalized_power


def test_wavelet_power_nonnegative() -> None:
    p = normalized_power([1 + 1j, 2 + 0j], 2.0)
    assert all(v >= 0 for v in p)
