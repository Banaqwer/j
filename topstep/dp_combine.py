"""Exact optimal daily policy for a Topstep-style Trading Combine, by value iteration.

Decision model
--------------
Each trading day the trader picks a daily profit target Delta and a daily stop
Lambda (both multiples of the grid step h) and a contract size k.  Intraday the
P&L is a Brownian motion per contract with (mu_1, sigma_1) per trade, so the
day resolves at +Delta with probability

    q = p_hit_upper(Delta, Lambda, gamma_1 / k),   gamma_1 = 2 mu_1 / sigma_1^2

and at -Lambda otherwise.  k is chosen automatically per (Delta, Lambda): the
smallest size that resolves the bet within `trades_per_day` on average when
gamma_1 >= 0 (timid is better in a favourable game), the largest allowed size
when gamma_1 < 0 (bold is better in an unfavourable game).

End-of-day bookkeeping (Topstep):
  * pass   if balance >= target AND best_day <= consistency_share * profit (if rule on)
           AND days >= min_days
  * bust   if the intraday balance touches the MLL (Lambda == cushion and the day loses)
  * MLL'   = min(lock_at, max(MLL, balance' - D))      (end-of-day trailing, locks at lock_at)

Consistency is tracked through the *required profit to pass*
    r = max(target, best_day / share)
which takes only a handful of values, instead of tracking best_day itself.

Objective:  maximise  E[ R_pass * 1{pass} - daily_fee * (trading days) ],
with an optional "quit" action (stop paying fees, value 0).
R_pass = 1, daily_fee = 0 gives the pure pass-probability maximiser.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence

import numpy as np

from .closed_form import p_hit_upper, expected_time_fixed
from .edge import Edge


@dataclass
class CombineSpec:
    target: float                   # profit target ($ above start)
    mll: float                      # maximum loss limit distance ($)
    lock_at: float = 0.0            # MLL stops trailing once it reaches start + lock_at
    consistency_share: Optional[float] = None  # best day must be <= share * profit, or None
    min_days: int = 0               # minimum trading days before passing
    max_contracts: int = 5          # scaling-plan cap used for the bold size
    daily_cap: Optional[float] = None  # max achievable |daily P&L| ($); None -> target + mll
    name: str = ""


@dataclass
class Action:
    delta: float
    lam: float
    k: int
    q: float
    s_w: np.ndarray = field(repr=False)
    s_l: np.ndarray = field(repr=False)
    pass_w: np.ndarray = field(repr=False)
    bust_l: np.ndarray = field(repr=False)
    feasible: np.ndarray = field(repr=False)


def _pick_size(delta: float, lam: float, edge: Edge, max_k: int):
    """Return (k, q) for a daily bet (+delta / -lam) or (None, None) if no size
    can resolve it within edge.trades_per_day on average."""
    mu1, s1 = edge.mu, edge.sigma
    feasible = []
    for k in range(1, max_k + 1):
        et = expected_time_fixed(delta, lam, k * mu1, k * s1)
        if et <= edge.trades_per_day:
            feasible.append(k)
    if not feasible:
        return None, None
    k = min(feasible) if edge.gamma >= 0 else max(feasible)
    g = edge.gamma / k
    return k, p_hit_upper(delta, lam, g)


class CombineDP:
    def __init__(self, spec: CombineSpec, edge: Edge, h: float = 100.0,
                 deltas: Optional[Sequence[float]] = None, lambdas: Optional[Sequence[float]] = None,
                 R_pass: float = 1.0, daily_fee: float = 0.0, allow_quit: bool = False):
        self.spec, self.edge, self.h = spec, edge, float(h)
        self.R_pass, self.daily_fee, self.allow_quit = R_pass, daily_fee, allow_quit
        T, D, s = spec.target, spec.mll, spec.consistency_share
        cap = spec.daily_cap if spec.daily_cap is not None else (T + D)
        if deltas is None:
            deltas = self._default_grid(cap, h)
        if lambdas is None:
            lambdas = self._default_grid(cap, h)
        self.deltas = sorted(set(float(x) for x in deltas))
        self.lambdas = sorted(set(float(x) for x in lambdas))
        for x in self.deltas + self.lambdas:
            if abs(x / h - round(x / h)) > 1e-9 or x <= 0:
                raise ValueError(f"action value {x} is not a positive multiple of the grid step h={h}")
        # required-profit levels r = max(T, delta/s)
        if s:
            rv = {T} | {d / s for d in self.deltas if d / s > T}
        else:
            rv = {T}
        self.r_values = np.array(sorted(rv))
        Bmax = float(np.ceil(self.r_values.max() / h) * h)
        self.Bmax = Bmax
        self.nb = int(round((Bmax + D) / h)) + 1
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
        self.d = self.idd
        self.alive = self.b > self.M
        self.actions: list[Action] = []
        self._build_actions()
        self.V: Optional[np.ndarray] = None
        self.policy: Optional[np.ndarray] = None

    @staticmethod
    def _default_grid(cap: float, h: float = 100.0) -> list[float]:
        """Multiples of h: every multiple up to 10h, then a coarser ladder (all multiples of h)."""
        fine = [h * i for i in range(1, 11)]
        coarse = [1200, 1500, 1750, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 6000, 7000, 8000, 9000,
                  10000, 12000, 14000, 16000]
        vals = set(x for x in fine if x <= cap)
        for x in coarse:
            if x <= cap and abs(x / h - round(x / h)) < 1e-9 and x > 10 * h:
                vals.add(float(x))
        return sorted(vals)

    def idx(self, ib, im, ir, idd):
        return ((ib * self.nm + im) * self.nr + ir) * self.nd + idd

    def _build_actions(self):
        sp, h = self.spec, self.h
        T, D, s = sp.target, sp.mll, sp.consistency_share
        for delta in self.deltas:
            for lam in self.lambdas:
                k, q = _pick_size(delta, lam, self.edge, sp.max_contracts)
                if k is None:
                    continue
                dsteps, lsteps = int(round(delta / h)), int(round(lam / h))
                cushion_steps = self.ib - self.im
                feasible = self.alive & (lsteps <= cushion_steps)
                # --- win branch
                ib_w = self.ib + dsteps
                ir_w = self.ir.copy()
                if s:
                    r_new = max(T, delta / s)
                    ir_w = np.maximum(ir_w, int(np.searchsorted(self.r_values, r_new)))
                d_w = np.minimum(self.idd + 1, self.nd - 1)
                b_w = -D + ib_w * h
                pass_w = (b_w >= self.r_values[ir_w] - 1e-9) & (d_w >= sp.min_days)
                ib_w = np.minimum(ib_w, self.nb - 1)
                b_w = -D + ib_w * h
                m_w = np.minimum(sp.lock_at, np.maximum(self.M, b_w - D))
                im_w = np.rint((m_w + D) / h).astype(int)
                s_w = self.idx(ib_w, im_w, ir_w, d_w)
                # --- lose branch
                ib_l = self.ib - lsteps
                bust_l = ib_l <= self.im
                ib_l = np.maximum(ib_l, 0)
                d_l = np.minimum(self.idd + 1, self.nd - 1)
                s_l = self.idx(ib_l, self.im, self.ir, d_l)
                self.actions.append(Action(delta, lam, k, q, s_w.astype(np.int32), s_l.astype(np.int32),
                                           pass_w, bust_l, feasible))
        if not self.actions:
            raise RuntimeError("no feasible actions; increase trades_per_day or max_contracts")

    # ------------------------------------------------------------------ solve
    def _policy_system(self, policy: np.ndarray, R: float, c: float):
        """Sparse (I - A) and rhs for the linear system V = A V + rhs under `policy`."""
        from scipy.sparse import coo_matrix, identity
        rows, cols, vals = [], [], []
        rhs = np.zeros(self.S)
        for ai, a in enumerate(self.actions):
            m = np.flatnonzero((policy == ai) & self.alive & a.feasible)
            if m.size == 0:
                continue
            mw = m[~a.pass_w[m]]
            rows.append(mw); cols.append(a.s_w[mw]); vals.append(np.full(mw.size, a.q))
            ml = m[~a.bust_l[m]]
            rows.append(ml); cols.append(a.s_l[ml]); vals.append(np.full(ml.size, 1.0 - a.q))
            rhs[m] = a.q * a.pass_w[m] * R - c
        if rows:
            A = coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                           shape=(self.S, self.S)).tocsr()
        else:
            A = coo_matrix((self.S, self.S)).tocsr()
        return (identity(self.S, format="csr") - A).tocsc(), rhs

    def _solve_linear(self, policy: np.ndarray, R: float, c: float) -> np.ndarray:
        from scipy.sparse.linalg import spsolve
        Msys, rhs = self._policy_system(policy, R, c)
        V = spsolve(Msys, rhs)
        return np.asarray(V).ravel()

    def _q_values(self, V: np.ndarray):
        """Return (best_value, best_action) of the one-step lookahead on V."""
        c, R = self.daily_fee, self.R_pass
        best = np.full(self.S, -np.inf)
        arg = np.full(self.S, -1, dtype=np.int32)
        for ai, a in enumerate(self.actions):
            vw = np.where(a.pass_w, R, V[a.s_w])
            vl = np.where(a.bust_l, 0.0, V[a.s_l])
            val = a.q * vw + (1.0 - a.q) * vl - c
            val = np.where(a.feasible, val, -np.inf)
            better = val > best + 1e-12
            best = np.where(better, val, best)
            arg = np.where(better, ai, arg)
        if self.allow_quit:
            qb = best < 0.0
            best = np.where(qb, 0.0, best)
            arg = np.where(qb, -1, arg)
        best = np.where(self.alive & np.isfinite(best), best, 0.0)
        return best, arg

    def solve(self, tol: float = 1e-9, max_iter: int = 200, verbose: bool = False):
        """Howard policy iteration (exact policy evaluation by sparse linear solve)."""
        V = np.zeros(self.S)
        _, policy = self._q_values(V)
        for it in range(max_iter):
            V_new = self._solve_linear(policy, self.R_pass, self.daily_fee)
            if self.allow_quit:
                V_new = np.where(policy == -1, 0.0, V_new)
            best, arg = self._q_values(V_new)
            # keep the current action unless a strictly better one exists (ensures convergence)
            cur = np.full(self.S, -np.inf)
            for ai, a in enumerate(self.actions):
                m = policy == ai
                if m.any():
                    vw = np.where(a.pass_w, self.R_pass, V_new[a.s_w])
                    vl = np.where(a.bust_l, 0.0, V_new[a.s_l])
                    cur[m] = (a.q * vw + (1.0 - a.q) * vl - self.daily_fee)[m]
            cur = np.where(policy == -1, 0.0, cur)
            change = best > cur + 1e-10
            new_policy = np.where(change, arg, policy)
            n_changed = int(np.sum(new_policy != policy))
            if verbose:
                print(f"PI iter {it}: {n_changed} actions changed, V0={V_new[self.fresh_state()]:.6f}")
            policy = new_policy
            if n_changed == 0:
                V = V_new
                break
            V = V_new
        self.V, self.policy = V, policy
        return V

    # --------------------------------------------------------------- evaluate
    def evaluate(self, policy: np.ndarray):
        """Pass probability and expected trading days for a state->action map
        (action index, -1 = quit).  Returns (P_pass, E_days) arrays over states."""
        P = self._solve_linear(policy, 1.0, 0.0)
        E = self._solve_linear(policy, 0.0, -1.0)
        P = np.where(policy == -1, 0.0, P)
        E = np.where(policy == -1, 0.0, E)
        return P, E

    def state_index(self, b: float = 0.0, M: Optional[float] = None, r: Optional[float] = None, d: int = 0) -> int:
        D, h = self.spec.mll, self.h
        if M is None:
            M = -D
        if r is None:
            r = self.spec.target
        ib = int(round((b + D) / h))
        im = int(round((M + D) / h))
        ir = int(np.searchsorted(self.r_values, r))
        return int(self.idx(ib, im, ir, min(d, self.nd - 1)))

    def fresh_state(self) -> int:
        return self.state_index()

    # ----------------------------------------------------------- fixed policies
    def policy_fixed(self, delta: float, lam: float) -> np.ndarray:
        """Always bet (+delta / -lam); if lam exceeds the cushion use the largest feasible stop."""
        return self._policy_from_rule(lambda b, M, r: (delta, lam))

    def policy_bold(self) -> np.ndarray:
        """One-shot: target the remaining distance to pass, stop at the MLL."""
        return self._policy_from_rule(lambda b, M, r: (r - b, b - M))

    def policy_timid(self) -> np.ndarray:
        return self.policy_fixed(self.h, self.h)

    def _policy_from_rule(self, rule: Callable[[float, float, float], tuple]) -> np.ndarray:
        pol = np.full(self.S, -1, dtype=np.int32)
        dl = np.array([(a.delta, a.lam) for a in self.actions])
        for sidx in np.flatnonzero(self.alive):
            want_d, want_l = rule(self.b[sidx], self.M[sidx], self.r[sidx])
            cushion = self.b[sidx] - self.M[sidx]
            want_l = min(want_l, cushion)
            # nearest feasible action: delta >= want_d (round up to grid), lam closest <= want_l
            cand = [i for i, a in enumerate(self.actions) if a.feasible[sidx]]
            if not cand:
                continue
            cd = np.array([self.actions[i].delta for i in cand])
            cl = np.array([self.actions[i].lam for i in cand])
            score = np.where(cd >= want_d - 1e-9, cd - want_d, 1e9) + np.abs(cl - want_l) * 1e-3
            pol[sidx] = cand[int(np.argmin(score))]
        return pol

    def describe_action(self, ai: int) -> str:
        if ai < 0:
            return "quit"
        a = self.actions[ai]
        return f"target +{a.delta:.0f} / stop -{a.lam:.0f} with {a.k} contract(s), q={a.q:.3f}"


def solve_combine(spec: CombineSpec, edge: Edge, h: float = 100.0, R_pass: float = 1.0,
                  daily_fee: float = 0.0, allow_quit: bool = False, **kw) -> dict:
    """Convenience: solve and evaluate optimal, bold and timid policies from the fresh state."""
    dp = CombineDP(spec, edge, h=h, R_pass=R_pass, daily_fee=daily_fee, allow_quit=allow_quit, **kw)
    dp.solve()
    s0 = dp.fresh_state()
    out = {"dp": dp, "V0": float(dp.V[s0]), "optimal_action": dp.describe_action(int(dp.policy[s0]))}
    for name, pol in (("optimal", dp.policy), ("bold", dp.policy_bold()), ("timid", dp.policy_timid())):
        P, E = dp.evaluate(pol)
        out[name] = {"P_pass": float(P[s0]), "E_days": float(E[s0])}
    return out
