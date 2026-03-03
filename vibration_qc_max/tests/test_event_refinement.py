from vibration.ephemeris.moon_events import bisection_refine


def test_bisection_refine() -> None:
    root = bisection_refine(lambda x: x - 1.5, 1.0, 2.0)
    assert abs(root - 1.5) < 0.001
