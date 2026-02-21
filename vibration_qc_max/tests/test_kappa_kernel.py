from vibration.ephemeris.geometry import kappa_from_orb


def test_kappa_positive() -> None:
    assert kappa_from_orb(2.0) > 0
