"""Finite-horizon optimal trade/payout policy for the Topstep Express Funded
Account (XFA), Standard payout path, by backward induction on exact day-P&L
distributions (see daymodel.py).

Verified mechanics modelled (help.topstep.com, Nov 2026):
  * balance starts at $0; MLL starts at -D and trails the END-OF-DAY balance,
    locking at $0 once the balance reaches D;
  * a payout needs 5 "winning days" (day Net P&L >= $150) since the last payout
    (the request day itself does not count), positive net profit since the last
    payout (first payout exempt), request <= 50% of balance, <= cap (50K: $2,000;
    $4,000 if a DLL was added at Combine checkout), >= $125; trader keeps 90%;
  * after EVERY payout the MLL is set to $0 permanently and the day count restarts;
  * Scaling Plan: max lots depend on the current balance (50K: 2 / 3 / 5 lots
    below $1,500 / $1,500-2,000 / above $2,000);
  * optional Daily Loss Limit caps the daily stop.

State (end of day): (b, M, ref, w)
    b    balance ($, grid step h)             M   MLL ($, grid; = 0 after first payout)
    ref  balance right after the last payout (None before the first payout)
    w    winning days since last payout (capped at w_required)
Actions: trade (Delta, Lambda) with the size chosen inside the Scaling-Plan cap of
         the current balance; payout; do nothing.
Objective: maximise expected (discounted) sum of net payouts over H trading days.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np

from .daymodel import DayOutcomes, choose_size
from .dp_combine import default_grid
from .edge import Edge


@dataclass
class FundedSpec:
    size: str = "50K"
    mll: float = 2000.0
    lock_at: float = 0.0
    win_threshold: float = 150.0
    w_required: int = 5
    cap_share: float = 0.5
    cap_abs: float = 2000.0
    min_payout: float = 125.0
    split: float = 0.9
    require_profit_since_last_payout: bool = True
    mll_to_zero_after_payout: bool = True
    scaling: tuple = ((1500.0, 2), (2000.0, 3), (float("inf"), 5))
    daily_loss_limit: Optional[float] = None
    daily_cap: Optional[float] = None
    consistency_share: Optional[float] = None   # Consistency path (40%) - handled by sim.py, not this DP
    path: str = "standard"
    name: str = ""

    def max_lots(self, balance):
        balance = np.asarray(balance, dtype=float)
        out = np.full(balance.shape, self.scaling[-1][1], dtype=int)
        for ub, lots in reversed(self.scaling):
            out = np.where(balance < ub, lots, out)
        return out


@dataclass
class FAction:
    delta: float
    lam: float
    lsteps: int
    by_cap: dict          # cap (max lots) -> DayOutcomes (or None)


class FundedDP:
    def __init__(self, spec: FundedSpec, edge: Edge, h: float = 100.0, Bmax: float = 10000.0,
                 horizon: int = 250, discount: float = 1.0,
                 deltas: Optional[Sequence[float]] = None, lambdas: Optional[Sequence[float]] = None,
                 coarse: bool = False):
        if spec.path != "standard":
            raise ValueError("FundedDP models the Standard payout path; use sim.run_funded for the Consistency path")
        self.spec, self.edge, self.h = spec, edge, float(h)
        self.H, self.beta = int(horizon), float(discount)
        D = spec.mll
        dcap = spec.daily_cap if spec.daily_cap is not None else max(2 * D, 2 * spec.cap_abs)
        lcap = max(D, spec.cap_abs) if spec.daily_cap is None else spec.daily_cap
        if spec.daily_loss_limit is not None:
            lcap = min(lcap, spec.daily_loss_limit)
        self.deltas = sorted(set(float(x) for x in (deltas or default_grid(dcap, h, coarse))))
        self.lambdas = sorted(set(float(x) for x in (lambdas or default_grid(lcap, h, coarse))))
        for x in self.deltas + self.lambdas:
            if abs(x / h - round(x / h)) > 1e-9 or x <= 0:
                raise ValueError(f"action value {x} is not a positive multiple of h={h}")
        if abs(spec.lock_at / h - round(spec.lock_at / h)) > 1e-9:
            raise ValueError("lock_at must be a multiple of h")
        self.caps = sorted({int(l) for _, l in spec.scaling})
        self.Bmax = float(np.ceil(Bmax / h) * h)
        self.nb = int(round((self.Bmax + D) / h)) + 1
        self.nm = int(round((spec.lock_at + D) / h)) + 1
        self.im_lock = self.nm - 1
        self.nref = int(round(self.Bmax / h)) + 1
        self.nw = spec.w_required + 1
        # ---- states
        states = []
        for ib in range(self.nb):
            for im in range(self.nm):
                if ib > im:
                    for iw in range(self.nw):
                        states.append((ib, im, 0, iw))
        im0 = self.im_lock
        for ib in range(im0 + 1, self.nb):
            for iref in range(1, self.nref):
                for iw in range(self.nw):
                    states.append((ib, im0, iref, iw))
        st = np.array(states, dtype=np.int32)
        self.ib, self.im, self.iref, self.iw = st[:, 0], st[:, 1], st[:, 2], st[:, 3]
        self.S = st.shape[0]
        self.lookup = -np.ones((self.nb, self.nm, self.nref, self.nw), dtype=np.int32)
        self.lookup[self.ib, self.im, self.iref, self.iw] = np.arange(self.S, dtype=np.int32)
        self.b = -D + self.ib * h
        self.M = -D + self.im * h
        self.ref = np.where(self.iref == 0, -np.inf, (self.iref - 1) * h)
        self.cap_state = spec.max_lots(self.b)
        self.cap_group = np.searchsorted(np.array(self.caps), self.cap_state)   # index into self.caps
        # ---- actions and outcome matrix
        self.actions: list[FAction] = []
        for delta in self.deltas:
            for lam in self.lambdas:
                by_cap = {cap: choose_size(delta, lam, edge, cap, h) for cap in self.caps}
                if all(v is None for v in by_cap.values()):
                    continue
                self.actions.append(FAction(delta, lam, int(round(lam / h)), by_cap))
        if not self.actions:
            raise RuntimeError("no feasible trade actions")
        ovals = sorted({int(o) for a in self.actions for v in a.by_cap.values() if v is not None for o in v.steps})
        self.o_values = np.array(ovals)
        o_index = {int(o): j for j, o in enumerate(self.o_values)}
        A, C, J = len(self.actions), len(self.caps), len(self.o_values)
        self.W = np.zeros((A * C, J))              # row = ai * C + ci
        self.row_ok = np.zeros((A, C), dtype=bool)
        for ai, a in enumerate(self.actions):
            for ci, cap in enumerate(self.caps):
                v = a.by_cap[cap]
                if v is None:
                    continue
                self.row_ok[ai, ci] = True
                for o, p in zip(v.steps, v.prob):
                    self.W[ai * C + ci, o_index[int(o)]] = p
        self.t_next = np.zeros((J, self.S), dtype=np.int32)
        self.t_bust = np.zeros((J, self.S), dtype=bool)
        for j, o in enumerate(self.o_values):
            s_n, bust = self.transition(int(o))
            self.t_next[j], self.t_bust[j] = s_n, bust
        lsteps = np.array([a.lsteps for a in self.actions])
        self.feas = (lsteps[:, None] <= (self.ib - self.im)[None, :]) & self.row_ok[:, self.cap_group]  # (A, S)
        self._build_payout()
        self.V = None
        self.policy = None
        self.policy_t = None

    def _lookup(self, ib, im, iref, iw):
        return self.lookup[np.clip(ib, 0, self.nb - 1), np.clip(im, 0, self.nm - 1),
                           np.clip(iref, 0, self.nref - 1), np.clip(iw, 0, self.nw - 1)]

    def transition(self, o_steps: int):
        sp, h, D = self.spec, self.h, self.spec.mll
        ib_n = self.ib + o_steps
        bust = ib_n <= self.im
        ib_n = np.clip(ib_n, 0, self.nb - 1)
        b_n = -D + ib_n * h
        m_n = np.minimum(sp.lock_at, np.maximum(self.M, b_n - D))
        im_n = np.rint((m_n + D) / h).astype(int)
        iw_n = np.minimum(self.iw + (1 if o_steps * h >= sp.win_threshold - 1e-9 else 0), self.nw - 1)
        s_n = self._lookup(ib_n, im_n, self.iref, iw_n)
        s_n = np.where(bust, 0, s_n)
        assert (s_n >= 0).all(), "transition left the state space"
        return s_n.astype(np.int32), bust

    def _build_payout(self):
        sp, h, D = self.spec, self.h, self.spec.mll
        A = np.minimum(sp.cap_share * self.b, sp.cap_abs)
        A = np.floor(A / h + 1e-9) * h
        eligible = (self.iw >= sp.w_required) & (self.b > 0) & (A >= sp.min_payout - 1e-9)
        if sp.require_profit_since_last_payout:
            eligible &= (self.iref == 0) | (self.b > self.ref + 1e-9)
        b_after = self.b - A
        ib_p = np.rint((b_after + D) / h).astype(int)
        im_p = np.full(self.S, self.im_lock) if sp.mll_to_zero_after_payout else self.im
        iref_p = np.rint(b_after / h).astype(int) + 1
        s_p = self._lookup(ib_p, im_p, iref_p, np.zeros(self.S, dtype=int))
        M_after = np.where(sp.mll_to_zero_after_payout, 0.0, self.M)
        terminal = eligible & (s_p < 0) & (b_after <= M_after + 1e-9)
        eligible &= (s_p >= 0) | terminal
        self.pay_A = np.where(eligible, A, 0.0)
        self.pay_eligible = eligible
        self.pay_terminal = terminal
        self.pay_next = np.where(eligible & ~terminal, s_p, 0).astype(np.int32)

    def _trade_values(self, V: np.ndarray) -> np.ndarray:
        """(A, S) value of each trade action from each state (−inf if infeasible)."""
        Vn = np.where(self.t_bust, 0.0, V[self.t_next])          # (J, S)
        Q = self.W @ Vn                                          # (A*C, S)
        C = len(self.caps)
        Q = Q.reshape(len(self.actions), C, self.S)
        Qs = Q[:, self.cap_group, np.arange(self.S)]             # (A, S): row matching the state's cap
        return np.where(self.feas, Qs, -np.inf)

    def solve(self, keep_policies: bool = True):
        V = np.zeros(self.S)
        pol_t = []
        ar = np.arange(self.S)
        for t in range(self.H - 1, -1, -1):
            Q = self.beta * self._trade_values(V)
            arg = np.argmax(Q, axis=0).astype(np.int32)
            best = Q[arg, ar]
            nothing = self.beta * V
            use_nothing = ~(best > nothing + 1e-12)
            best = np.where(use_nothing, nothing, best)
            arg = np.where(use_nothing, -2, arg)
            vp = self.spec.split * self.pay_A + self.beta * np.where(self.pay_terminal, 0.0, V[self.pay_next])
            vp = np.where(self.pay_eligible, vp, -np.inf)
            better = vp > best + 1e-12
            best = np.where(better, vp, best)
            arg = np.where(better, -1, arg)
            V = np.where(np.isfinite(best), best, 0.0)
            if keep_policies:
                pol_t.append(arg)
        self.V, self.policy = V, arg
        self.policy_t = pol_t[::-1] if keep_policies else None
        return V

    def state_index(self, b: float = 0.0, M: Optional[float] = None, ref: Optional[float] = None, w: int = 0) -> int:
        D, h = self.spec.mll, self.h
        if M is None:
            M = -D
        ib = int(round((b + D) / h))
        im = int(round((M + D) / h))
        iref = 0 if ref is None else int(round(ref / h)) + 1
        return int(self.lookup[ib, im, iref, min(w, self.nw - 1)])

    def fresh_state(self) -> int:
        return self.state_index()

    def action_k(self, ai: int, s: int) -> int:
        a = self.actions[ai]
        v = a.by_cap[self.caps[self.cap_group[s]]]
        return int(v.k) if v is not None else 0

    def describe_action(self, ai: int, s: Optional[int] = None) -> str:
        if ai == -1:
            return "request payout"
        if ai == -2:
            return "do nothing"
        a = self.actions[ai]
        if s is None:
            return f"target +{a.delta:.0f} / stop -{a.lam:.0f}"
        v = a.by_cap[self.caps[self.cap_group[s]]]
        return (f"target +{a.delta:.0f} / stop -{a.lam:.0f} with {v.k} contract(s), "
                f"P(win day)={v.p_win:.3f}, unresolved={v.p_unresolved:.2f}")

    def simulate_policy(self, n_paths: int = 20000, seed: int = 0, record: bool = False) -> dict:
        """Monte Carlo of the time-dependent optimal policy inside the day-outcome model."""
        if self.policy_t is None:
            self.solve(keep_policies=True)
        rng = np.random.default_rng(seed)
        s = np.full(n_paths, self.fresh_state(), dtype=np.int64)
        alive = np.ones(n_paths, bool)
        paid = np.zeros(n_paths)
        n_payouts = np.zeros(n_paths, int)
        first_payout_day = np.full(n_paths, -1)
        C = len(self.caps)
        Wc = np.cumsum(self.W, axis=1)
        for t in range(self.H):
            pol = self.policy_t[t][s]
            m = alive & (pol == -1)
            if m.any():
                paid[m] += self.spec.split * self.pay_A[s[m]]
                n_payouts[m] += 1
                first_payout_day[m & (first_payout_day < 0)] = t
                term = self.pay_terminal[s[m]]
                idx_m = np.flatnonzero(m)
                alive[idx_m[term]] = False
                s[m] = self.pay_next[s[m]]
            m = alive & (pol >= 0)
            if m.any():
                ai = pol[m]
                sm = s[m]
                rows = ai * C + self.cap_group[sm]
                u = rng.random(m.sum())
                j = (Wc[rows] < u[:, None]).sum(axis=1)
                j = np.minimum(j, len(self.o_values) - 1)
                bust = self.t_bust[j, sm]
                nxt = self.t_next[j, sm]
                idx_m = np.flatnonzero(m)
                alive[idx_m[bust]] = False
                s[m] = nxt
        return {
            "mean_payout": float(paid.mean()),
            "median_payout": float(np.median(paid)),
            "p_any_payout": float((n_payouts > 0).mean()),
            "p_bust": float((~alive).mean()),
            "mean_n_payouts": float(n_payouts.mean()),
            "payout_quantiles": {q: float(np.quantile(paid, q)) for q in (0.1, 0.25, 0.5, 0.75, 0.9, 0.99)},
            "mean_first_payout_day": float(first_payout_day[first_payout_day >= 0].mean()) if (first_payout_day >= 0).any() else float("nan"),
            "paid": paid if record else None,
        }


def funded_spec_from_rules(size: str = "50K", dll: bool = False) -> FundedSpec:
    from .rules import xfa_params
    p = xfa_params(size, "standard", dll)
    return FundedSpec(size=size, mll=p["mll"], lock_at=p["lock_at"], win_threshold=p["win_threshold"],
                      w_required=p["w_required"], cap_share=p["cap_share"], cap_abs=p["cap_abs"],
                      min_payout=p["min_payout"], split=p["split"], scaling=p["scaling"],
                      daily_loss_limit=p["daily_loss_limit"], path="standard",
                      name=f"XFA {size} standard{' +DLL' if dll else ''}")
