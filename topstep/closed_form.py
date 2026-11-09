"""Closed-form hitting probabilities for evaluation-style barrier problems.

Model
-----
Cumulative P&L  X_t  is a Brownian motion with drift mu and volatility sigma
(per unit of "trade time").  Every barrier-hitting probability below depends on
(mu, sigma) only through

    gamma = 2 * mu / sigma**2         [units: 1/$]

because the scale function of the diffusion is s(x) = exp(-gamma x).
Scaling every position by k multiplies mu by k and sigma**2 by k**2, so
gamma -> gamma / k:  bigger size = closer to a fair game (gamma -> 0).

Sign conventions: barriers are given as positive distances.  All functions
start the process at 0 (= account starting balance, or the current balance).
"""
from __future__ import annotations

import math


def gamma_from_moments(mu: float, sigma: float) -> float:
    """gamma = 2 mu / sigma^2."""
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    return 2.0 * mu / (sigma * sigma)


def p_hit_upper(a: float, b: float, gamma: float) -> float:
    """P(BM with scale parameter gamma hits +a before -b | start 0).

    Classical gambler's-ruin for a diffusion:
        gamma == 0 :  b / (a + b)
        gamma != 0 :  (1 - e^{-gamma b}) / (1 - e^{-gamma (a+b)})
    Implemented with expm1 for numerical stability in both signs of gamma.
    """
    if a <= 0:
        return 1.0
    if b <= 0:
        return 0.0
    x = gamma * (a + b)
    if abs(x) < 1e-12:
        return b / (a + b)
    if gamma > 0:
        return (-math.expm1(-gamma * b)) / (-math.expm1(-gamma * (a + b)))
    g = -gamma
    return math.expm1(g * b) / math.expm1(g * (a + b))


def expected_time_fixed(a: float, b: float, mu: float, sigma: float) -> float:
    """E[time to hit +a or -b] for BM(mu, sigma) from 0 (Wald / Dynkin)."""
    if a <= 0 or b <= 0:
        return 0.0
    if abs(mu) < 1e-15:
        return a * b / (sigma * sigma)
    p = p_hit_upper(a, b, gamma_from_moments(mu, sigma))
    return (a * p - b * (1.0 - p)) / mu


def p_target_before_trailing_drawdown(T: float, D: float, gamma: float) -> float:
    """P(running max reaches +T before the drawdown from the running max exceeds D),
    for a continuously trailing drawdown (Taylor 1975 / Lehoczky 1977).

        gamma == 0 :  exp(-T / D)
        gamma != 0 :  exp(- gamma T / (e^{gamma D} - 1))

    Derivation: while the running max sits at level m, the process must reach
    m + dm before m - D.  That has probability 1 - (gamma e^{-gamma D}/(1-e^{-gamma D})) dm
    + o(dm); the product over T/dm such steps gives the exponential above.
    """
    if T <= 0:
        return 1.0
    if D <= 0:
        return 0.0
    if abs(gamma * D) < 1e-12:
        return math.exp(-T / D)
    return math.exp(-gamma * T / math.expm1(gamma * D))


def p_pass_topstep_continuous(T: float, D: float, gamma: float, lock_at: float = 0.0) -> float:
    """Continuous-time approximation of the Topstep pass probability.

    Rules modelled: the Maximum Loss Limit (MLL) trails the running maximum at
    distance D until the MLL reaches `lock_at` (relative to the starting
    balance, Topstep: 0 = the starting balance), after which it is fixed.
    The target is +T.

    If T <= D + lock_at the target is hit while the MLL is still trailing:
        P = p_target_before_trailing_drawdown(T, D, gamma)
    otherwise the max must first reach D + lock_at (MLL locks at lock_at), and
    then the process must reach T before falling to lock_at:
        P = p_target_before_trailing_drawdown(D + lock_at, D, gamma)
            * p_hit_upper(T - (D + lock_at), D, gamma)
    """
    L = D + lock_at
    if T <= L:
        return p_target_before_trailing_drawdown(T, D, gamma)
    return p_target_before_trailing_drawdown(L, D, gamma) * p_hit_upper(T - L, D, gamma)


def bold_play_bound(T: float, D: float, gamma: float = 0.0) -> float:
    """Upper bound on P(pass) for ANY strategy when the game is fair or subfair
    (gamma <= 0): the single-bet bold play value p_hit_upper(T, D, gamma).

    For gamma == 0 this is D / (T + D) and follows from optional stopping:
    E[X_tau] <= 0 with X_tau >= T on pass and X_tau >= -D always, so
    P(pass) * T - (1 - P(pass)) * D <= 0.
    """
    return p_hit_upper(T, D, min(gamma, 0.0)) if gamma <= 0 else p_hit_upper(T, D, gamma)


def kelly_fraction(p_win: float, reward: float, loss: float) -> float:
    """Kelly fraction for a binary bet (win +reward w.p. p, lose -loss otherwise),
    expressed as fraction of bankroll risked per trade (f* = p/loss_frac - q/reward_frac
    rearranged):  f* = (p * reward - (1-p) * loss) / (reward * loss) * loss ... simplified:
        edge per unit risked  e = (p*reward - (1-p)*loss) / loss
        odds b = reward / loss
        f* = e / b = p - (1-p)/b
    Returns 0 if non-positive.
    """
    if loss <= 0 or reward <= 0:
        raise ValueError("reward and loss must be positive")
    b = reward / loss
    f = p_win - (1.0 - p_win) / b
    return max(f, 0.0)


def grossman_zhou_fraction(mu_ann: float, sigma_ann: float, max_dd: float, r: float = 0.0) -> float:
    """Grossman-Zhou (1993) drawdown-constrained growth-optimal exposure:
    the fraction of (wealth - floor) to hold in the risky asset is the Merton
    fraction (mu - r)/sigma^2; expressed as a fraction of total wealth at the
    high-water mark it is (1 - max_dd) * ... Here we return the Merton fraction
    applied to the cushion above the floor (1 - max_dd) * W_max:
        exposure(W) = ((mu - r) / sigma^2) * (W - (1 - max_dd) * W_max)
    and the function returns the multiplier (mu - r)/sigma^2.
    """
    return (mu_ann - r) / (sigma_ann * sigma_ann)
