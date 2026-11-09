import math
import numpy as np
import pytest

from topstep import closed_form as cf


def test_fair_gamblers_ruin():
    assert cf.p_hit_upper(3000, 2000, 0.0) == pytest.approx(0.4)
    assert cf.p_hit_upper(6000, 3000, 0.0) == pytest.approx(1 / 3)


def test_drift_limits():
    # strong positive drift -> ~1, strong negative -> ~0
    assert cf.p_hit_upper(1000, 1000, 0.05) > 0.999
    assert cf.p_hit_upper(1000, 1000, -0.05) < 0.001
    # symmetry: P_up(a,b,g) = 1 - P_up(b,a,-g)
    for g in (-0.003, -0.0007, 0.0007, 0.003):
        assert cf.p_hit_upper(700, 300, g) == pytest.approx(1 - cf.p_hit_upper(300, 700, -g))


def test_continuity_in_gamma():
    a, b = 3000, 2000
    assert cf.p_hit_upper(a, b, 1e-13) == pytest.approx(cf.p_hit_upper(a, b, 0.0), abs=1e-9)
    assert cf.p_hit_upper(a, b, 1e-6) == pytest.approx(cf.p_hit_upper(a, b, 0.0), abs=1e-3)


def test_trailing_drawdown_driftless():
    assert cf.p_target_before_trailing_drawdown(2000, 2000, 0.0) == pytest.approx(math.exp(-1))
    assert cf.p_target_before_trailing_drawdown(3000, 2000, 0.0) == pytest.approx(math.exp(-1.5))
    # continuity at gamma -> 0
    assert cf.p_target_before_trailing_drawdown(3000, 2000, 1e-9) == pytest.approx(math.exp(-1.5), abs=1e-6)


def test_topstep_lock_composite():
    # 50K: T=3000, D=2000, lock at 0 -> e^-1 * 2000/3000
    assert cf.p_pass_topstep_continuous(3000, 2000, 0.0) == pytest.approx(math.exp(-1) * 2 / 3)
    # 100K: T=6000, D=3000 -> e^-1 * 1/2
    assert cf.p_pass_topstep_continuous(6000, 3000, 0.0) == pytest.approx(math.exp(-1) * 0.5)
    # if target below lock level, pure trailing formula applies
    assert cf.p_pass_topstep_continuous(1500, 2000, 0.0) == pytest.approx(math.exp(-0.75))


def test_bold_bound_dominates_timid_when_fair():
    for T, D in ((3000, 2000), (6000, 3000), (9000, 4500)):
        assert cf.bold_play_bound(T, D, 0.0) > cf.p_pass_topstep_continuous(T, D, 0.0)


@pytest.mark.slow
def test_monte_carlo_matches_trailing_formula():
    """Brute-force check of exp(-gamma T/(e^{gamma D}-1)) with a fine random walk."""
    rng = np.random.default_rng(1)
    T, D = 1000.0, 1000.0
    for gamma in (0.0, 0.002, -0.002):
        n = 20000
        dt_sigma = 5.0  # $ per step
        mu = gamma * dt_sigma ** 2 / 2  # mu = gamma sigma^2 / 2 per step
        steps = 400000
        x = np.zeros(n)
        mx = np.zeros(n)
        alive = np.ones(n, bool)
        passed = np.zeros(n, bool)
        for _ in range(steps):
            inc = rng.choice([-dt_sigma, dt_sigma], size=n) + mu
            x[alive] += inc[alive]
            mx = np.maximum(mx, x)
            hit = alive & (x >= T)
            passed |= hit
            bust = alive & (mx - x >= D)
            alive &= ~(hit | bust)
            if not alive.any():
                break
        est = passed.mean()
        exact = cf.p_target_before_trailing_drawdown(T, D, gamma)
        assert abs(est - exact) < 0.012, (gamma, est, exact)
