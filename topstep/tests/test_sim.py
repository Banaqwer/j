import numpy as np
import pytest

from topstep import closed_form as cf
from topstep.sim import run_combine, bold_combine_policy, fixed_policy
from topstep.dp_combine import CombineSpec
from topstep.edge import Edge


def test_bold_sim_matches_gamblers_ruin_fine_steps():
    # tiny trades (R=L=$10) so the discrete walk is close to the continuous barrier problem
    e = Edge(0.5, 10, 10, 0.0, trades_per_day=100000)
    spec = CombineSpec(target=3000, mll=2000, max_contracts=1)
    res = run_combine(spec, e, bold_combine_policy(k=1), n_accounts=4000, max_days=5, seed=1)
    assert res["P_unresolved"] == 0.0
    assert abs(res["P_pass"] - 0.4) < 0.03


def test_timid_sim_near_discrete_trailing_formula():
    e = Edge(0.5, 100, 100, 0.0, trades_per_day=10000)
    spec = CombineSpec(target=3000, mll=2000, max_contracts=1)
    res = run_combine(spec, e, fixed_policy(100, 100, 1), n_accounts=20000, max_days=5000, seed=2)
    D, T, h = 2000, 3000, 100
    exact = (D / (D + h)) ** (D / h) * cf.p_hit_upper(T - D, D, 0.0)
    assert res["P_unresolved"] < 0.01
    assert abs(res["P_pass"] - exact) < 0.015


def test_funded_trade_level_zero_edge_respects_martingale_bound():
    from topstep.sim import run_funded, dp_funded_policy
    from topstep.dp_funded import FundedDP, funded_spec_from_rules
    e = Edge(0.5, 100, 100, 0.0, trades_per_day=30)
    spec = funded_spec_from_rules("50K")
    dp = FundedDP(spec, e, h=100.0, Bmax=6000, horizon=40)
    dp.solve(keep_policies=True)
    res = run_funded(spec, e, dp_funded_policy(dp), n_accounts=20000, horizon=40, seed=5)
    assert res["mean_payout"] <= 0.9 * 2000 + 60.0
    assert res["p_any_payout"] > 0.05
