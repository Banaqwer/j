from vibration.stats.placebos import circular_shift


def test_circular_shift() -> None:
    x = [1, 2, 3]
    assert circular_shift(x, 1) == [3, 1, 2]
