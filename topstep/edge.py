"""Trader edge models: per-trade statistics -> (mu, sigma, gamma) per contract."""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Edge:
    """A binary-outcome trade model, per ONE contract.

    p_win   : probability a trade wins
    reward  : $ won on a winning trade (per contract, before costs)
    loss    : $ lost on a losing trade (per contract, before costs)
    cost_rt : round-turn commissions + fees per contract ($)
    trades_per_day : maximum trades the trader can take in a session
    """
    p_win: float
    reward: float
    loss: float
    cost_rt: float = 0.0
    trades_per_day: int = 10
    name: str = ""

    @property
    def mu(self) -> float:
        """Expected $ per trade per contract, net of costs."""
        return self.p_win * self.reward - (1.0 - self.p_win) * self.loss - self.cost_rt

    @property
    def sigma(self) -> float:
        """Std-dev of $ per trade per contract (net of costs; costs are deterministic)."""
        m_gross = self.p_win * self.reward - (1.0 - self.p_win) * self.loss
        var = self.p_win * self.reward ** 2 + (1.0 - self.p_win) * self.loss ** 2 - m_gross ** 2
        return math.sqrt(max(var, 1e-18))

    @property
    def gamma(self) -> float:
        """2 mu / sigma^2 per contract (1/$)."""
        return 2.0 * self.mu / (self.sigma ** 2)

    @property
    def sharpe_per_trade(self) -> float:
        return self.mu / self.sigma

    def daily_sharpe(self) -> float:
        return self.sharpe_per_trade * math.sqrt(self.trades_per_day)

    def annual_sharpe(self, days: int = 252) -> float:
        return self.daily_sharpe() * math.sqrt(days)

    def describe(self) -> str:
        return (f"{self.name or 'edge'}: p_win={self.p_win:.3f} R={self.reward:.0f} L={self.loss:.0f} "
                f"cost={self.cost_rt:.2f} -> mu={self.mu:.2f}$/trade sigma={self.sigma:.1f} "
                f"gamma={self.gamma:+.5f}/$ per-trade Sharpe={self.sharpe_per_trade:+.3f} "
                f"annual Sharpe~{self.annual_sharpe():+.2f} ({self.trades_per_day} trades/day)")


def edge_from_sharpe(sharpe_per_trade: float, sigma: float = 100.0, cost_rt: float = 0.0,
                     trades_per_day: int = 10, name: str = "") -> Edge:
    """Build a symmetric (reward == loss) binary edge with the requested NET
    per-trade Sharpe ratio mu/sigma.  Solves for p_win."""
    # symmetric payoff S: mu_gross = S(2p-1), sigma ~= S sqrt(1-(2p-1)^2)
    # target: (mu_gross - cost)/sigma = sharpe.  Solve numerically by bisection on p.
    lo, hi = 0.0, 1.0
    for _ in range(200):
        p = 0.5 * (lo + hi)
        e = Edge(p, sigma, sigma, cost_rt, trades_per_day, name)
        if e.sharpe_per_trade < sharpe_per_trade:
            lo = p
        else:
            hi = p
    return Edge(0.5 * (lo + hi), sigma, sigma, cost_rt, trades_per_day, name)


# Reference edges.  reward/loss are per ES-mini contract ($50/pt): a 2-point
# stop/target is $100.  cost_rt ~ $4-6 for ES on TopstepX; MES ~ $1.2.
ZERO_EDGE_FREE = Edge(0.50, 100.0, 100.0, 0.0, 10, "zero edge, no costs (theoretical)")
ZERO_EDGE = Edge(0.50, 100.0, 100.0, 5.0, 10, "zero edge after $5 RT costs (coin flip)")
WEAK_EDGE = Edge(0.53, 100.0, 100.0, 5.0, 10, "weak edge (53% at 1R)")
MODEST_EDGE = Edge(0.55, 100.0, 100.0, 5.0, 10, "modest edge (55% at 1R)")
STRONG_EDGE = Edge(0.60, 100.0, 100.0, 5.0, 10, "strong edge (60% at 1R)")
NEGATIVE_EDGE = Edge(0.47, 100.0, 100.0, 5.0, 10, "negative edge (47% at 1R)")
PRESETS = {
    "zero_free": ZERO_EDGE_FREE,
    "zero": ZERO_EDGE,
    "weak": WEAK_EDGE,
    "modest": MODEST_EDGE,
    "strong": STRONG_EDGE,
    "negative": NEGATIVE_EDGE,
}
