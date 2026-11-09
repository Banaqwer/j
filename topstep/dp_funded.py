"""Finite-horizon optimal trade/payout policy for the Topstep Express Funded
Account (XFA), Standard payout path, by backward induction.

Verified mechanics modelled (help.topstep.com, Nov 2026):
  * balance starts at $0; MLL starts at -D and trails the END-OF-DAY balance,
    locking at $0 once the balance reaches D;
  * a payout needs 5 "winning days" (day Net P&L >= $150) since the last payout
    (the request day itself does not count), positive net profit since the last
    payout (first payout exempt), request <= 50% of balance, <= cap (50K: $2,000;
    $4,000 if a DLL was added at Combine checkout), >= $125; trader keeps 90%;
  * after EVERY payout the MLL is set to $0 permanently and the winning-day count restarts;
  * Scaling Plan: max lots depend on the current balance (50K: 2 / 3 / 5 lots
    below $1,500 / $1,500-2,000 / above $2,000);
  * optional Daily Loss Limit caps the daily stop.

State (end of day): (b, M, ref, w)
    b    balance ($, grid step h)             M   MLL ($, grid; = 0 after first payout)
    ref  balance right after the last payout (None before the first payout)
    w    winning days since last payout (capped at w_required)
Actions: trade (Delta, Lambda) -> +Delta w.p. q, else -Lambda; size chosen automatically
         within the Scaling-Plan cap;  payout;  do nothing.
Objective: maximise expected (discounted) sum of payouts over H trading days.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence

import numpy as np

from .closed_form import p_hit_upper, expected_time_fixed
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
    q: np.ndarray = field(repr=False)        # per-state win probability (size depends on state)
    k: np.ndarray = field(repr=False)        # per-state contracts used
    s_w: np.ndarray = field(repr=False)
    s_l: np.ndarray = field(repr=False)
    bust_l: np.ndarray = field(repr=False)
    feasible: np.ndarray = field(repr=False)


def _size_table(delta: float, lam: float, edge: Edge, kmax: int):
    """For each allowed max size 1..kmax return (k_used, q) or (0, nan) if infeasible."""
    mu1, s1 = edge.mu, edge.sigma
    feas = [k for k in range(1, kmax + 1) if expected_time_fixed(delta, lam, k * mu1, k * s1) <= edge.trades_per_day]
    table = {}
    for cap in range(1, kmax + 1):
        f = [k for k in feas if k <= cap]
        if not f:
            table[cap] = (0, float("nan"))
        else:
            k = min(f) if edge.gamma >= 0 else max(f)
            table[cap] = (k, p_hit_upper(delta, lam, edge.gamma / k))
    return table


class FundedDP:
    def __init__(self, spec: FundedSpec, edge: Edge, h: float = 100.0, Bmax: float = 10000.0,
                 horizon: int = 250, discount: float = 1.0,
                 deltas: Optional[Sequence[float]] = None, lambdas: Optional[Sequence[float]] = None):
        if spec.path != "standard":
            raise ValueError("FundedDP models the Standard payout path; use sim.run_funded for the Consistency path")
        self.spec, self.edge, self.h = spec, edge, float(h)
        self.H, self.beta = int(horizon), float(discount)
        D = spec.mll
        cap = spec.daily_cap if spec.daily_cap is not None else max(2 * D, 2 * spec.cap_abs)
        from .dp_combine import CombineDP
        self.deltas = sorted(set(float(x) for x in (deltas or CombineDP._default_grid(cap, h))))
        lam_cap = max(D, spec.cap_abs) if spec.daily_cap is None else spec.daily_cap
        if spec.daily_loss_limit is not None:
            lam_cap = min(lam_cap, spec.daily_loss_limit)
        self.lambdas = sorted(set(float(x) for x in (lambdas or CombineDP._default_grid(lam_cap, h))))
        for x in self.deltas + self.lambdas:
            if abs(x / h - round(x / h)) > 1e-9 or x <= 0:
                raise ValueError(f"action value {x} is not a positive multiple of h={h}")
        self.Bmax = float(np.ceil(Bmax / h) * h)
        self.nb = int(round((self.Bmax + D) / h)) + 1          # b = -D + ib h
        self.nm = int(round((spec.lock_at + D) / h)) + 1       # M = -D + im h
        self.im_lock = self.nm - 1
        self.nref = int(round(self.Bmax / h)) + 1              # iref = 0 -> none; else ref = (iref-1) h
        self.nw = spec.w_required + 1
        # ---- enumerate valid states
        states = []
        # pre-first-payout: any M, ref none, b > M
        for ib in range(self.nb):
            for im in range(self.nm):
                if ib > im:
                    for iw in range(self.nw):
                        states.append((ib, im, 0, iw))
        # post-first-payout: M = 0 (locked), ref known, b > 0
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
        self.kmax_state = spec.max_lots(self.b)
        self.actions: list[FAction] = []
        self._build_actions()
        self._build_payout()
        self.V = None
        self.policy = None
        self.policy_t = None

    def _lookup(self, ib, im, iref, iw):
        idx = self.lookup[np.clip(ib, 0, self.nb - 1), np.clip(im, 0, self.nm - 1),
                          np.clip(iref, 0, self.nref - 1), np.clip(iw, 0, self.nw - 1)]
        return idx

    def _build_actions(self):
        sp, h, D = self.spec, self.h, self.spec.mll
        kmax_all = int(max(l for _, l in sp.scaling))
        for delta in self.deltas:
            for lam in self.lambdas:
                table = _size_table(delta, lam, self.edge, kmax_all)
                k_arr = np.array([table[int(c)][0] for c in range(1, kmax_all + 1)])
                q_arr = np.array([table[int(c)][1] for c in range(1, kmax_all + 1)])
                k_state = k_arr[self.kmax_state - 1]
                q_state = q_arr[self.kmax_state - 1]
                if not (k_state > 0).any():
                    continue
                dsteps, lsteps = int(round(delta / h)), int(round(lam / h))
                feasible = (k_state > 0) & (lsteps <= (self.ib - self.im))
                # win branch
                ib_w = np.minimum(self.ib + dsteps, self.nb - 1)
                b_w = -D + ib_w * h
                m_w = np.minimum(sp.lock_at, np.maximum(self.M, b_w - D))
                im_w = np.rint((m_w + D) / h).astype(int)
                iw_w = np.minimum(self.iw + (1 if delta >= sp.win_threshold else 0), self.nw - 1)
                s_w = self._lookup(ib_w, im_w, self.iref, iw_w)
                # lose branch
                ib_l = self.ib - lsteps
                bust_l = ib_l <= self.im
                s_l = self._lookup(np.maximum(ib_l, 0), self.im, self.iref, self.iw)
                s_l = np.where(bust_l, 0, s_l)
                assert (s_w[feasible] >= 0).all(), "win transition left the state space"
                assert (s_l[feasible & ~bust_l] >= 0).all(), "lose transition left the state space"
                self.actions.append(FAction(delta, lam, np.where(k_state > 0, q_state, 0.0).astype(np.float64),
                                            k_state.astype(np.int8), s_w.astype(np.int32), s_l.astype(np.int32),
                                            bust_l, feasible))
        if not self.actions:
            raise RuntimeError("no feasible trade actions")

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
        terminal = eligible & (s_p < 0) & (b_after <= M_after + 1e-9)   # withdrawal empties the account
        eligible &= (s_p >= 0) | terminal
        self.pay_A = np.where(eligible, A, 0.0)
        self.pay_eligible = eligible
        self.pay_terminal = terminal
        self.pay_next = np.where(eligible & ~terminal, s_p, 0).astype(np.int32)

    def solve(self, keep_policies: bool = True):
        V = np.zeros(self.S)
        pol_t = []
        for t in range(self.H - 1, -1, -1):
            best = self.beta * V            # do nothing
            arg = np.full(self.S, -2, dtype=np.int32)
            for ai, a in enumerate(self.actions):
                vl = np.where(a.bust_l, 0.0, V[a.s_l])
                val = self.beta * (a.q * V[a.s_w] + (1.0 - a.q) * vl)
                val = np.where(a.feasible, val, -np.inf)
                better = val > best + 1e-12
                best = np.where(better, val, best)
                arg = np.where(better, ai, arg)
            vp = self.spec.split * self.pay_A + self.beta * np.where(self.pay_terminal, 0.0, V[self.pay_next])
            vp = np.where(self.pay_eligible, vp, -np.inf)
            better = vp > best + 1e-12
            best = np.where(better, vp, best)
            arg = np.where(better, -1, arg)
            V = best
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

    def describe_action(self, ai: int, s: Optional[int] = None) -> str:
        if ai == -1:
            return "request payout"
        if ai == -2:
            return "do nothing"
        a = self.actions[ai]
        if s is None:
            return f"target +{a.delta:.0f} / stop -{a.lam:.0f}"
        return f"target +{a.delta:.0f} / stop -{a.lam:.0f} with {a.k[s]} contract(s), q={a.q[s]:.3f}"

    def simulate_policy(self, n_paths: int = 20000, seed: int = 0, record: bool = False) -> dict:
        """Monte Carlo of the time-dependent optimal policy inside the binary-day model."""
        if self.policy_t is None:
            self.solve(keep_policies=True)
        rng = np.random.default_rng(seed)
        s = np.full(n_paths, self.fresh_state(), dtype=np.int64)
        alive = np.ones(n_paths, bool)
        paid = np.zeros(n_paths)
        n_payouts = np.zeros(n_paths, int)
        first_payout_day = np.full(n_paths, -1)
        a_q = np.stack([a.q for a in self.actions])
        a_sw = np.stack([a.s_w for a in self.actions])
        a_sl = np.stack([a.s_l for a in self.actions])
        a_bust = np.stack([a.bust_l for a in self.actions])
        for t in range(self.H):
            pol = self.policy_t[t][s]
            u = rng.random(n_paths)
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
                win = u[m] < a_q[ai, sm]
                bust = (~win) & a_bust[ai, sm]
                s[m] = np.where(win, a_sw[ai, sm], a_sl[ai, sm])
                idx_m = np.flatnonzero(m)
                alive[idx_m[bust]] = False
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
