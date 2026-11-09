import math
import pytest

from topstep import closed_form as cf
from topstep.dp_combine import CombineDP, CombineSpec
from topstep.edge import Edge, ZERO_EDGE_FREE, MODEST_EDGE, NEGATIVE_EDGE

SPEC50 = CombineSpec(target=3000, mll=2000, lock_at=0.0, max_contracts=5)


def test_bold_one_day_matches_gamblers_ruin():
    for edge in (ZERO_EDGE_FREE, NEGATIVE_EDGE):
        e = Edge(edge.p_win, edge.reward, edge.loss, edge.cost_rt, trades_per_day=10000)
        dp = CombineDP(SPEC50, e, h=100.0)
        P, E = dp.evaluate(dp.policy_bold())
        s0 = dp.fresh_state()
        k = 5 if e.gamma < 0 else 1
        exact = cf.p_hit_upper(3000, 2000, e.gamma / k)
        assert P[s0] == pytest.approx(exact, abs=1e-6)
        assert E[s0] == pytest.approx(1.0, abs=1e-6)


def test_timid_matches_discrete_trailing_product():
    e = Edge(0.5, 100, 100, 0.0, trades_per_day=10000)
    h = 100.0
    dp = CombineDP(SPEC50, e, h=h)
    P, _ = dp.evaluate(dp.policy_timid())
    D, T = 2000, 3000
    exact = (D / (D + h)) ** (D / h) * cf.p_hit_upper(T - D, D, 0.0)
    assert P[dp.fresh_state()] == pytest.approx(exact, abs=1e-6)
    # and it converges to the continuous formula as h -> 0 (h=50 closer than h=100)
    cont = cf.p_pass_topstep_continuous(T, D, 0.0)
    dp50 = CombineDP(SPEC50, e, h=50.0)
    P50, _ = dp50.evaluate(dp50.policy_timid())
    assert abs(P50[dp50.fresh_state()] - cont) < abs(P[dp.fresh_state()] - cont)


def test_optimal_respects_bold_bound_when_fair_and_beats_both_when_favourable():
    e0 = Edge(0.5, 100, 100, 0.0, trades_per_day=10000)
    dp = CombineDP(SPEC50, e0, h=100.0)
    dp.solve()
    s0 = dp.fresh_state()
    assert dp.V[s0] <= cf.bold_play_bound(3000, 2000, 0.0) + 1e-6
    assert dp.V[s0] == pytest.approx(0.4, abs=1e-6)  # fair game: bold play optimal, value D/(T+D)
    e1 = MODEST_EDGE
    dp1 = CombineDP(SPEC50, e1, h=100.0)
    dp1.solve()
    Pb, _ = dp1.evaluate(dp1.policy_bold())
    Pt, _ = dp1.evaluate(dp1.policy_timid())
    assert dp1.V[dp1.fresh_state()] >= max(Pb[dp1.fresh_state()], Pt[dp1.fresh_state()]) - 1e-9


def test_consistency_rule_blocks_single_day_pass():
    spec = CombineSpec(target=3000, mll=2000, consistency_share=0.5, max_contracts=5)
    e = Edge(0.5, 100, 100, 0.0, trades_per_day=10000)
    dp = CombineDP(spec, e, h=100.0)
    dp.solve()
    v = dp.V[dp.fresh_state()]
    assert v < 0.4  # one-shot bold play is no longer available
    assert v > 0.2
