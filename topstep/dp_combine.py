"""Exact optimal daily policy for a Topstep-style Trading Combine, by policy iteration.

Decision model
--------------
Each trading day the trader picks a daily profit target Delta and a daily stop
Lambda (multiples of the grid step h); the contract size is chosen by
daymodel.choose_size.  The day's P&L then follows the EXACT distribution of the
stopped trade walk (overshoot and unresolved sessions included), rounded to the
grid (daymodel.day_outcomes).

End-of-day bookkeeping (Topstep):
  * pass   if balance >= max(target, best_day / 0.55)   [consistency target]
           AND days >= min_days
  * bust   if the balance reaches the MLL (also intraday: the stop never exceeds the cushion)
  * MLL'   = min(lock_at, max(MLL, balance' - D))       (end-of-day trailing, locks at lock_at)

The consistency target is tracked through the required profit r = max(T, best_day / share).

Objective:  maximise  E[ R_pass * 1{pass} - daily_fee * (trading days) ],
with an optional "quit" action.  R_pass = 1, daily_fee = 0 -> pass-probability maximiser.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence

import numpy as np

from .daymodel import DayOutcomes, choose_size
from .edge import Edge


@dataclass
class CombineSpec:
    target: float
    mll: float
    lock_at: float = 0.0
    consistency_share: Optional[float] = None
    min_days: int = 0
    max_contracts: int = 5
    daily_cap: Optional[float] = None       # caps the daily stop (optional Daily Loss Limit)
    name: str = ""


@dataclass
class Action:
    delta: float
    lam: float
    k: int
    out: DayOutcomes
    lsteps: int
    q: float          # P(day won) for display


def default_grid(cap: float, h: float, coarse: bool = False) -> list[float]:
    fine = [h * i for i in range(1, 11)]
    if coarse:
        fine = [h * i for i in (1, 2, 3, 4, 5, 6, 8, 10)]
    ladder = [1200, 1500, 1750, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 6000, 7000, 8000, 9000,
              10000, 12000, 14000, 16000]
    if coarse:
        ladder = [1500, 2000, 2500, 3000, 4000, 5000, 6000, 8000, 10000, 12000, 16000]
    vals = set(x for x in fine if x <= cap)
    for x in ladder:
        if x <= cap and abs(x / h - round(x / h)) < 1e-9 and x > max(fine):
            vals.add(float(x))
    return sorted(vals)


class CombineDP:
    def __init__(self, spec: CombineSpec, edge: Edge, h: float = 100.0,
                 deltas: Optional[Sequence[float]] = None, lambdas: Optional[Sequence[float]] = None,
                 R_pass: float = 1.0, daily_fee: float = 0.0, allow_quit: bool = False, coarse: bool = False):
        self.spec, self.edge, self.h = spec, edge, float(h)
        self.R_pass, self.daily_fee, self.allow_quit = R_pass, daily_fee, allow_quit
        T, D, s = spec.target, spec.mll, spec.consistency_share
        dcap = T
        lcap = D if spec.daily_cap is None else min(D, spec.daily_cap)
        self.deltas = sorted(set(float(x) for x in (deltas or default_grid(dcap, h, coarse))))
        self.lambdas = sorted(set(float(x) for x in (lambdas or default_grid(lcap, h, coarse))))
        for x in self.deltas + self.lambdas:
            if abs(x / h - round(x / h)) > 1e-9 or x <= 0:
                raise ValueError(f"action value {x} is not a positive multiple of h={h}")
        # --- build day distributions first (they determine the largest single-day profit)
        self._raw_actions = []
        omax = 0
        for delta in self.deltas:
            for lam in self.lambdas:
                o = choose_size(delta, lam, edge, spec.max_contracts, h)
                if o is None:
                    continue
                self._raw_actions.append((delta, lam, o))
                omax = max(omax, int(o.steps.max()))
        if not self._raw_actions:
            raise RuntimeError("no feasible actions")
        # --- required-profit levels r = max(T, v / s) for single-day profits v on the grid
        if s:
            rv = {T} | {v * h / s for v in range(1, omax + 1) if v * h / s > T + 1e-9}
        else:
            rv = {T}
        self.r_values = np.array(sorted(rv))
        self.Bmax = float(np.ceil(self.r_values.max() / h) * h)
        self.nb = int(round((self.Bmax + D) / h)) + 1
        self.nm = int(round((spec.lock_at + D) / h)) + 1
        self.nr = len(self.r_values)
        self.nd = spec.min_days + 1 if spec.min_days > 0 else 1
        ib, im, ir, idd = np.meshgrid(np.arange(self.nb), np.arange(self.nm), np.arange(self.nr),
                                      np.arange(self.nd), indexing="ij")
        self.ib, self.im, self.ir, self.idd = (a.ravel() for a in (ib, im, ir, idd))
        self.S = self.ib.size
        self.b = -D + self.ib * h
        self.M = -D + self.im * h
        self.r = self.r_values[self.ir]
        self.alive = self.b > self.M
        # map single-day profit (grid steps) -> required-profit index
        self.ir_of_step = np.zeros(omax + 1, dtype=int)
        if s:
            for v in range(1, omax + 1):
                rv_ = v * h / s
                self.ir_of_step[v] = int(np.searchsorted(self.r_values, rv_ - 1e-9)) if rv_ > T + 1e-9 else 0
        self.actions: list[Action] = []
        for delta, lam, o in self._raw_actions:
            self.actions.append(Action(delta, lam, o.k, o, int(round(lam / h)), o.p_win))
        # outcome matrix: W[a, j] = P(day P&L = o_j | action a); transitions precomputed per distinct o_j
        self.o_values = np.array(sorted({int(o) for a in self.actions for o in a.out.steps}))
        o_index = {int(o): j for j, o in enumerate(self.o_values)}
        self.W = np.zeros((len(self.actions), len(self.o_values)))
        for ai, a in enumerate(self.actions):
            for o, p in zip(a.out.steps, a.out.prob):
                self.W[ai, o_index[int(o)]] = p
        self.t_next = np.zeros((len(self.o_values), self.S), dtype=np.int32)
        self.t_pass = np.zeros((len(self.o_values), self.S), dtype=bool)
        self.t_bust = np.zeros((len(self.o_values), self.S), dtype=bool)
        for j, o in enumerate(self.o_values):
            s_n, passed, bust = self.transition(int(o))
            self.t_next[j], self.t_pass[j], self.t_bust[j] = s_n, passed, bust
        self.feas = np.stack([self.feasible(a) for a in self.actions])   # (A, S)
        self.V: Optional[np.ndarray] = None
        self.policy: Optional[np.ndarray] = None

    # ------------------------------------------------------------- transitions
    def idx(self, ib, im, ir, idd):
        return ((ib * self.nm + im) * self.nr + ir) * self.nd + idd

    def feasible(self, a: Action) -> np.ndarray:
        return self.alive & (a.lsteps <= (self.ib - self.im))

    def transition(self, o_steps: int):
        """For a day P&L of o_steps grid units: (next_index, is_pass, is_bust) over all states."""
        sp, h, D = self.spec, self.h, self.spec.mll
        ib_n = self.ib + o_steps
        bust = ib_n <= self.im
        ib_n = np.clip(ib_n, 0, self.nb - 1)
        b_n = -D + ib_n * h
        ir_n = np.maximum(self.ir, self.ir_of_step[o_steps]) if o_steps > 0 else self.ir
        d_n = np.minimum(self.idd + 1, self.nd - 1)
        passed = (~bust) & (b_n >= self.r_values[ir_n] - 1e-9) & (d_n >= sp.min_days)
        m_n = np.minimum(sp.lock_at, np.maximum(self.M, b_n - D))
        im_n = np.rint((m_n + D) / h).astype(int)
        s_n = self.idx(ib_n, im_n, ir_n, d_n)
        return s_n, passed, bust

    def _continuations(self, V: np.ndarray, R: float) -> np.ndarray:
        """(n_o, S): value after a day with P&L o_j from each state."""
        Vn = V[self.t_next]
        Vn = np.where(self.t_bust, 0.0, Vn)
        Vn = np.where(self.t_pass, R, Vn)
        return Vn

    def _all_action_values(self, V: np.ndarray, R: float, c: float) -> np.ndarray:
        Q = self.W @ self._continuations(V, R) - c        # (A, S)
        return np.where(self.feas, Q, -np.inf)

    def _action_value(self, a: Action, V: np.ndarray, R: float, c: float) -> np.ndarray:
        ai = self.actions.index(a)
        return self._all_action_values(V, R, c)[ai]

    def _q_values(self, V: np.ndarray):
        Q = self._all_action_values(V, self.R_pass, self.daily_fee)
        arg = np.argmax(Q, axis=0).astype(np.int32)
        best = Q[arg, np.arange(self.S)]
        arg = np.where(np.isfinite(best), arg, -1)
        if self.allow_quit:
            qb = best < 0.0
            best = np.where(qb, 0.0, best)
            arg = np.where(qb, -1, arg)
        best = np.where(self.alive & np.isfinite(best), best, 0.0)
        return best, arg

    def _policy_system(self, policy: np.ndarray, R: float, c: float):
        from scipy.sparse import coo_matrix, identity
        rows, cols, vals = [], [], []
        rhs = np.zeros(self.S)
        for ai, a in enumerate(self.actions):
            m = np.flatnonzero((policy == ai) & self.alive & self.feasible(a))
            if m.size == 0:
                continue
            rhs[m] -= c
            for o, p in zip(a.out.steps, a.out.prob):
                s_n, passed, bust = self.transition(int(o))
                cont = m[~(passed[m] | bust[m])]
                rows.append(cont); cols.append(s_n[cont]); vals.append(np.full(cont.size, p))
                rhs[m] += p * R * passed[m]
        if rows:
            A = coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                           shape=(self.S, self.S)).tocsr()
        else:
            A = coo_matrix((self.S, self.S)).tocsr()
        return (identity(self.S, format="csr") - A).tocsc(), rhs

    def _solve_linear(self, policy: np.ndarray, R: float, c: float) -> np.ndarray:
        from scipy.sparse.linalg import spsolve
        Msys, rhs = self._policy_system(policy, R, c)
        return np.asarray(spsolve(Msys, rhs)).ravel()

    # ------------------------------------------------------------------ solve
    def solve(self, max_iter: int = 100, verbose: bool = False):
        """Howard policy iteration with exact sparse policy evaluation."""
        V = np.zeros(self.S)
        _, policy = self._q_values(V)
        for it in range(max_iter):
            V = self._solve_linear(policy, self.R_pass, self.daily_fee)
            if self.allow_quit:
                V = np.where(policy == -1, 0.0, V)
            best, arg = self._q_values(V)
            Q = self._all_action_values(V, self.R_pass, self.daily_fee)
            cur = np.where(policy >= 0, Q[np.maximum(policy, 0), np.arange(self.S)], 0.0)
            change = best > cur + 1e-10
            new_policy = np.where(change, arg, policy)
            n_changed = int(np.sum(new_policy != policy))
            if verbose:
                print(f"PI iter {it}: {n_changed} changed, V0={V[self.fresh_state()]:.6f}")
            policy = new_policy
            if n_changed == 0:
                break
        V = self._solve_linear(policy, self.R_pass, self.daily_fee)
        if self.allow_quit:
            V = np.where(policy == -1, 0.0, V)
        self.V, self.policy = V, policy
        return V

    def evaluate(self, policy: np.ndarray):
        """(P_pass, E_days) over states for a state->action map (-1 = quit)."""
        P = self._solve_linear(policy, 1.0, 0.0)
        E = self._solve_linear(policy, 0.0, -1.0)
        P = np.where((policy == -1) | ~self.alive, 0.0, P)
        E = np.where((policy == -1) | ~self.alive, 0.0, E)
        return P, E

    # ----------------------------------------------------------------- helpers
    def state_index(self, b: float = 0.0, M: Optional[float] = None, r: Optional[float] = None, d: int = 0) -> int:
        D, h = self.spec.mll, self.h
        if M is None:
            M = -D
        if r is None:
            r = self.spec.target
        ib = int(round((b + D) / h))
        im = int(round((M + D) / h))
        ir = int(np.searchsorted(self.r_values, r - 1e-9))
        return int(self.idx(ib, im, min(ir, self.nr - 1), min(d, self.nd - 1)))

    def fresh_state(self) -> int:
        return self.state_index()

    def policy_fixed(self, delta: float, lam: float) -> np.ndarray:
        return self._policy_from_rule(lambda b, M, r: (delta, lam))

    def policy_bold(self) -> np.ndarray:
        return self._policy_from_rule(lambda b, M, r: (r - b, b - M))

    def policy_timid(self) -> np.ndarray:
        return self.policy_fixed(self.h, self.h)

    def _policy_from_rule(self, rule: Callable[[float, float, float], tuple]) -> np.ndarray:
        pol = np.full(self.S, -1, dtype=np.int32)
        feas = np.stack([self.feasible(a) for a in self.actions])  # (A, S)
        cd = np.array([a.delta for a in self.actions])
        cl = np.array([a.lam for a in self.actions])
        for sidx in np.flatnonzero(self.alive):
            want_d, want_l = rule(self.b[sidx], self.M[sidx], self.r[sidx])
            want_l = min(want_l, self.b[sidx] - self.M[sidx])
            f = feas[:, sidx]
            if not f.any():
                continue
            score = np.where(cd >= want_d - 1e-9, cd - want_d, 1e9) + np.abs(cl - want_l) * 1e-3
            score = np.where(f, score, np.inf)
            pol[sidx] = int(np.argmin(score))
        return pol

    def describe_action(self, ai: int) -> str:
        if ai < 0:
            return "quit"
        a = self.actions[ai]
        return (f"target +{a.delta:.0f} / stop -{a.lam:.0f} with {a.k} contract(s), "
                f"P(win day)={a.out.p_win:.3f}, unresolved={a.out.p_unresolved:.2f}")
