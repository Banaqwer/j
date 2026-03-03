from vibration.ephemeris.geometry import circ_dist, wrap360


def test_wrap360() -> None:
    assert wrap360(361.0) == 1.0


def test_circ_dist() -> None:
    assert circ_dist(350, 10) == 20
