from vibration.features.fft_locked import fft_power


def test_fft_power_len() -> None:
    x = [float(i) for i in range(8)]
    assert len(fft_power(x)) == 5
