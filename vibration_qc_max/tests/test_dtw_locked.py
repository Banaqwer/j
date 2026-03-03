from vibration.features.dtw_locked import z_norm


def test_z_norm_zero_mean() -> None:
    z = z_norm([1.0, 2.0, 3.0])
    assert abs(sum(z) / len(z)) < 1e-8
