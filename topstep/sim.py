"""Trade-level Monte Carlo of the full Topstep pipeline:
Trading Combine -> (pass) -> Express Funded Account -> payouts.

Unlike the DP modules (binary day outcomes), this engine simulates every trade
(binary win/loss per contract with costs), so days can end unresolved, targets
can be overshot, the intraday balance can touch the MLL mid-day, and the real
best-day / winning-day bookkeeping is applied.  It is the validation layer for
the DP policies and the place to test any heuristic policy.

Policies are callables  policy(state) -> (delta, lam, k)  evaluated once per day
from the end-of-day state arrays (vectorised over accounts), or the special
value (0, 0, 0) meaning "request payout today / do not trade".
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np

from .dp_combine import CombineSpec
from .dp_funded import FundedSpec
from .edge import Edge


@dataclass
class DayState:
    b: np.ndarray        # balance - start
    M: np.ndarray        # MLL - start
    best: np.ndarray     # best day P&L so far
    w: np.ndarray        # winning days since last payout (funded) / total (combine)
    days: np.ndarray     # trading days so far
    paid: np.ndarray     # cumulative payouts received (funded)
    n_payouts: np.ndarray


def _simulate_day(rng: np.random.Generator, edge: Edge, delta: np.ndarray, lam: np.ndarray, k: np.ndarray,
                  cushion: np.ndarray, active: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Simulate one session for all active accounts.  Returns (day_pnl, busted).
    Trades are taken until +delta or -lam is reached (per account), or
    edge.trades_per_day trades are used, or the running P&L touches -cushion
    (MLL breach, busted)."""
    n = delta.size
    pnl = np.zeros(n)
    busted = np.zeros(n, bool)
    live = active.copy()
    unit_w = (edge.reward - edge.cost_rt) * k
    unit_l = (edge.loss + edge.cost_rt) * k
    for _ in range(edge.trades_per_day):
        if not live.any():
            break
        win = rng.random(n) < edge.p_win
        step = np.where(win, unit_w, -unit_l)
        pnl = np.where(live, pnl + step, pnl)
        hit_mll = live & (pnl <= -cushion + 1e-9)
        busted |= hit_mll
        done = live & ((pnl >= delta - 1e-9) | (pnl <= -lam + 1e-9) | hit_mll)
        live &= ~done
    return pnl, busted


def run_combine(spec: CombineSpec, edge: Edge, policy: Callable, n_accounts: int = 20000,
                max_days: int = 500, seed: int = 0, monthly_fee: float = 0.0, days_per_month: int = 21) -> dict:
    rng = np.random.default_rng(seed)
    n = n_accounts
    st = DayState(np.zeros(n), np.full(n, -spec.mll), np.zeros(n), np.zeros(n, int), np.zeros(n, int),
                  np.zeros(n), np.zeros(n, int))
    passed = np.zeros(n, bool)
    busted = np.zeros(n, bool)
    for day in range(max_days):
        active = ~(passed | busted)
        if not active.any():
            break
        delta, lam, k = policy(st, spec)
        cushion = st.b - st.M
        lam = np.minimum(lam, cushion)
        pnl, bust_now = _simulate_day(rng, edge, delta, lam, k, cushion, active)
        bn = st.b + np.where(active, pnl, 0.0)
        busted |= active & (bust_now | (bn <= st.M + 1e-9))
        st.days += active
        still = active & ~busted
        st.best = np.where(still, np.maximum(st.best, pnl), st.best)
        st.b = np.where(still, bn, st.b)
        # EOD trailing MLL with lock
        st.M = np.where(still, np.minimum(spec.lock_at, np.maximum(st.M, st.b - spec.mll)), st.M)
        ok = st.b >= spec.target - 1e-9
        if spec.consistency_share:
            ok &= st.best <= spec.consistency_share * st.b + 1e-9
        ok &= st.days >= spec.min_days
        passed |= still & ok
    fees = monthly_fee * np.ceil(np.maximum(st.days, 1) / days_per_month)
    return {
        "P_pass": float(passed.mean()),
        "P_bust": float(busted.mean()),
        "P_unresolved": float((~(passed | busted)).mean()),
        "E_days": float(st.days.mean()),
        "E_days_given_pass": float(st.days[passed].mean()) if passed.any() else float("nan"),
        "E_fees": float(fees.mean()),
        "state": st, "passed": passed, "busted": busted,
    }


def run_funded(spec: FundedSpec, edge: Edge, policy: Callable, n_accounts: int = 20000, horizon: int = 250,
               seed: int = 0) -> dict:
    """Trade-level simulation of the XFA (Standard or Consistency payout path).

    policy(st, spec) -> (delta, lam, k) per account; delta == 0 requests a payout,
    delta < 0 sits out the day."""
    rng = np.random.default_rng(seed)
    n = n_accounts
    st = DayState(np.zeros(n), np.full(n, -spec.mll), np.zeros(n), np.zeros(n, int), np.zeros(n, int),
                  np.zeros(n), np.zeros(n, int))
    st.ref = np.zeros(n)                 # balance right after the last payout (0 before any payout)
    st.had_payout = np.zeros(n, bool)
    busted = np.zeros(n, bool)
    first_payout_day = np.full(n, -1)
    consistency = bool(spec.consistency_share)
    for day in range(horizon):
        active = ~busted
        if not active.any():
            break
        delta, lam, k = policy(st, spec)
        k = np.minimum(k, spec.max_lots(st.b))
        want_payout = active & (delta == 0)
        if want_payout.any():
            A = np.minimum(spec.cap_share * st.b, spec.cap_abs)
            elig = want_payout & (st.w >= spec.w_required) & (st.b > 0) & (A >= spec.min_payout - 1e-9)
            if spec.require_profit_since_last_payout:
                elig &= (~st.had_payout) | (st.b > st.ref + 1e-9)
            if consistency:
                window_profit = st.b - st.ref
                elig &= (window_profit > 0) & (st.best <= spec.consistency_share * window_profit + 1e-9)
            st.paid = np.where(elig, st.paid + spec.split * A, st.paid)
            st.b = np.where(elig, st.b - A, st.b)
            if spec.mll_to_zero_after_payout:
                st.M = np.where(elig, 0.0, st.M)
            st.ref = np.where(elig, st.b, st.ref)
            st.n_payouts += elig
            st.w = np.where(elig, 0, st.w)
            st.best = np.where(elig, 0.0, st.best)       # consistency window resets
            first_payout_day = np.where(elig & (first_payout_day < 0), day, first_payout_day)
            st.had_payout |= elig
            busted |= elig & (st.b <= st.M + 1e-9)       # a 100% withdrawal closes the account
        trade = active & ~busted & (delta > 0)
        cushion = st.b - st.M
        lam = np.minimum(lam, cushion)
        if spec.daily_loss_limit is not None:
            lam = np.minimum(lam, spec.daily_loss_limit)
        pnl, bust_now = _simulate_day(rng, edge, delta, lam, k, cushion, trade)
        bn = st.b + np.where(trade, pnl, 0.0)
        busted |= trade & (bust_now | (bn <= st.M + 1e-9))
        st.days += active
        still = trade & ~busted
        st.best = np.where(still, np.maximum(st.best, pnl), st.best)
        if consistency:
            st.w = np.where(still, st.w + 1, st.w)                       # trading days
        else:
            st.w = np.where(still & (pnl >= spec.win_threshold - 1e-9), st.w + 1, st.w)
        st.b = np.where(still, bn, st.b)
        st.M = np.where(still, np.minimum(spec.lock_at, np.maximum(st.M, st.b - spec.mll)), st.M)
    paid = st.paid
    return {
        "mean_payout": float(paid.mean()),
        "median_payout": float(np.median(paid)),
        "p_any_payout": float((st.n_payouts > 0).mean()),
        "p_bust": float(busted.mean()),
        "mean_n_payouts": float(st.n_payouts.mean()),
        "payout_quantiles": {q: float(np.quantile(paid, q)) for q in (0.1, 0.25, 0.5, 0.75, 0.9, 0.99)},
        "mean_first_payout_day": float(first_payout_day[first_payout_day >= 0].mean()) if (first_payout_day >= 0).any() else float("nan"),
        "state": st, "busted": busted,
    }


# ----------------------------------------------------------------------------- policies
def fixed_policy(delta: float, lam: float, k: int = 1) -> Callable:
    def pol(st: DayState, spec):
        n = st.b.size
        return np.full(n, float(delta)), np.full(n, float(lam)), np.full(n, int(k))
    return pol


def bold_combine_policy(k: int = 5) -> Callable:
    """Target the remaining distance to the profit target in one day, stop at the MLL."""
    def pol(st: DayState, spec: CombineSpec):
        need = spec.target - st.b
        if spec.consistency_share:
            need = np.maximum(need, st.best / spec.consistency_share - st.b)
        return np.maximum(need, 1.0), st.b - st.M, np.full(st.b.size, int(k))
    return pol


def dp_combine_policy(dp) -> Callable:
    """Look up the solved CombineDP policy by (b, M, r) at end of day."""
    def pol(st: DayState, spec: CombineSpec):
        h = dp.h
        D = spec.mll
        ib = np.clip(np.rint((st.b + D) / h).astype(int), 0, dp.nb - 1)
        im = np.clip(np.rint((st.M + D) / h).astype(int), 0, dp.nm - 1)
        if spec.consistency_share:
            r = np.maximum(spec.target, st.best / spec.consistency_share)
            ir = np.clip(np.searchsorted(dp.r_values, r - 1e-9), 0, dp.nr - 1)
        else:
            ir = np.zeros_like(ib)
        idd = np.minimum(st.days, dp.nd - 1)
        s = dp.idx(ib, im, ir, idd)
        ai = dp.policy[s]
        delta = np.array([dp.actions[a].delta if a >= 0 else 1.0 for a in ai])
        lam = np.array([dp.actions[a].lam if a >= 0 else 1.0 for a in ai])
        k = np.array([dp.actions[a].k if a >= 0 else 1 for a in ai])
        return delta, lam, k
    return pol


def dp_funded_policy(dp) -> Callable:
    """Look up the solved FundedDP policy (time-dependent) from the sim state."""
    counter = {"t": 0}

    def pol(st: DayState, spec: FundedSpec):
        h, D = dp.h, spec.mll
        ib = np.clip(np.rint((st.b + D) / h).astype(int), 0, dp.nb - 1)
        im = np.clip(np.rint((st.M + D) / h).astype(int), 0, dp.nm - 1)
        iref = np.where(st.had_payout, np.clip(np.rint(st.ref / h).astype(int) + 1, 1, dp.nref - 1), 0)
        iw = np.minimum(st.w, dp.nw - 1)
        s = dp.lookup[ib, im, iref, iw]
        t = min(counter["t"], dp.H - 1)
        counter["t"] += 1
        table = dp.policy_t[t] if dp.policy_t is not None else dp.policy
        ai = np.where(s >= 0, table[np.maximum(s, 0)], -2)
        n = st.b.size
        delta = np.full(n, -1.0)
        lam = np.zeros(n)
        k = np.ones(n, dtype=int)
        tr = ai >= 0
        if tr.any():
            idx = np.flatnonzero(tr)
            delta[idx] = [dp.actions[a].delta for a in ai[idx]]
            lam[idx] = [dp.actions[a].lam for a in ai[idx]]
            k[idx] = [max(int(dp.actions[a].k[si]), 1) for a, si in zip(ai[idx], s[idx])]
        delta[ai == -1] = 0.0
        return delta, lam, k
    return pol
