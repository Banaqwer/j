import math


def wrap360(x: float) -> float:
    return x % 360.0


def circ_dist(a: float, b: float) -> float:
    diff = abs(wrap360(a) - wrap360(b))
    return min(diff, 360.0 - diff)


def kappa_from_orb(orb_deg: float) -> float:
    return math.log(0.5) / (math.cos(math.radians(orb_deg)) - 1.0)
