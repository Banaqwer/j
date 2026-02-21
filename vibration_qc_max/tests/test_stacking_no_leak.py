from vibration.models.stacking_timeseries import is_time_ordered


def test_is_time_ordered() -> None:
    assert is_time_ordered([1, 2, 3])
    assert not is_time_ordered([2, 1, 3])
