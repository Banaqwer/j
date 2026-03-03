from collections.abc import Callable


def bisection_refine(
    func: Callable[[float], float],
    lo: float,
    hi: float,
    tol_minutes: float = 1.0,
) -> float:
    tol_days = tol_minutes / (24.0 * 60.0)
    f_lo, f_hi = func(lo), func(hi)
    if f_lo == 0:
        return lo
    if f_hi == 0:
        return hi
    if f_lo * f_hi > 0:
        raise ValueError("Bracket does not contain a sign change")
    while (hi - lo) > tol_days:
        mid = (lo + hi) / 2.0
        f_mid = func(mid)
        if f_lo * f_mid <= 0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2.0
