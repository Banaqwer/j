import numpy as np
import pytest

from topstep.dp_funded import FundedDP, FundedSpec, funded_spec_from_rules
from topstep.edge import Edge


def test_zero_edge_payouts_bounded_by_drawdown_allowance():
    """Optional stopping: fair game => E[gross payouts] <= D, so E[net] <= 0.9 D."""
    e = Edge(0.5, 100, 100, 0.0, trades_per_day=10000)
    spec = funded_spec_from_rules("50K")
    dp = FundedDP(spec, e, h=100.0, Bmax=8000, horizon=120)
    v0 = dp.solve(keep_policies=False)[dp.fresh_state()]
    assert 0 < v0 <= 0.9 * 2000 + 1e-6
    # removing payout frictions cannot reduce the value
    spec2 = FundedSpec(mll=2000, lock_at=0, win_threshold=0, w_required=0, cap_share=1.0, cap_abs=1e9,
                       min_payout=0, split=0.9, require_profit_since_last_payout=False,
                       scaling=((float("inf"), 5),))
    dp2 = FundedDP(spec2, e, h=100.0, Bmax=8000, horizon=120)
    v2 = dp2.solve(keep_policies=False)[dp2.fresh_state()]
    assert v2 >= v0 - 1e-6
    assert v2 <= 0.9 * 2000 + 1e-6


def test_simulation_matches_value():
    e = Edge(0.55, 100, 100, 5.0, trades_per_day=20)
    spec = funded_spec_from_rules("50K")
    dp = FundedDP(spec, e, h=100.0, Bmax=8000, horizon=60)
    dp.solve(keep_policies=True)
    v0 = dp.V[dp.fresh_state()]
    sim = dp.simulate_policy(n_paths=40000, seed=3)
    assert abs(sim["mean_payout"] - v0) < 0.03 * max(v0, 100.0) + 20.0


def test_scaling_plan_lots():
    spec = funded_spec_from_rules("50K")
    assert list(spec.max_lots([0, 1499, 1500, 1999, 2000, 5000])) == [2, 2, 3, 3, 5, 5]
