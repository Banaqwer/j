"""Verified Topstep rule parameters (as of 2026-11-09), with sources.

Every number here was read from an official Topstep help-center article in
November 2026 and cross-checked; see docs/TOPSTEP_RULES.md for the cited
rule-set and its open uncertainties.  Rules change often: re-verify before use.

Sources (official):
  Combine parameters   https://help.topstep.com/en/articles/8284197-trading-combine-parameters
  Consistency (55%)    https://help.topstep.com/en/articles/8284208-consistency-at-topstep
  Maximum Loss Limit   https://help.topstep.com/en/articles/8284204-what-is-the-maximum-loss-limit
  Pricing / resets     https://help.topstep.com/en/articles/14289835-topstep-pricing-and-payment-questions
  XFA parameters       https://help.topstep.com/en/articles/8284215-express-funded-account-parameters
  Payout policy        https://help.topstep.com/en/articles/8284233-topstep-payout-policy
  Scaling plan         https://help.topstep.com/en/articles/8284223-what-is-the-scaling-plan
  Commissions          https://help.topstep.com/en/articles/8284213-what-are-the-commissions-and-fees
  Prohibited conduct   https://help.topstep.com/en/articles/10296582-prohibited-conduct
  Responsible Trading  https://help.topstep.com/en/articles/13620045-what-is-the-responsible-trading-program
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .dp_combine import CombineSpec

AS_OF = "2026-11-09"

# ---------------------------------------------------------------- Trading Combine
# target / MLL by size; MLL trails end-of-day and locks at the starting balance;
# best day must be <= 55% of (adjusted) profit target  <=>  profit >= best_day / 0.55.
COMBINE_PARAMS = {
    "50K": dict(target=3000.0, mll=2000.0, max_contracts=5),
    "100K": dict(target=6000.0, mll=3000.0, max_contracts=10),
    "150K": dict(target=9000.0, mll=4500.0, max_contracts=15),
}
COMBINE_CONSISTENCY_SHARE = 0.55
COMBINE_DLL = {"50K": 1000.0, "100K": 2000.0, "150K": 3000.0}   # optional, chosen at checkout


def combine_spec(size: str = "50K", consistency: bool = True, dll: bool = False) -> CombineSpec:
    p = COMBINE_PARAMS[size]
    return CombineSpec(target=p["target"], mll=p["mll"], lock_at=0.0,
                       consistency_share=COMBINE_CONSISTENCY_SHARE if consistency else None,
                       min_days=0, max_contracts=p["max_contracts"],
                       daily_cap=COMBINE_DLL[size] if dll else None,
                       name=f"Combine {size}{' +DLL' if dll else ''}")


@dataclass(frozen=True)
class Fees:
    monthly: float          # Combine subscription per 30 days
    reset: float            # reset price (each monthly rebill also grants one reset credit)
    activation: float       # one-time XFA activation fee
    back2funded: float      # reactivation of an XFA lost before its first payout (<= 2 times)
    path: str


FEES = {
    # Standard path: cheaper subscription, $149 activation per XFA
    ("50K", "standard"): Fees(49.0, 49.0, 149.0, 599.0, "standard"),
    ("100K", "standard"): Fees(99.0, 99.0, 149.0, 699.0, "standard"),
    ("150K", "standard"): Fees(199.0, 199.0, 149.0, 829.0, "standard"),
    # No-Activation-Fee path
    ("50K", "noaf"): Fees(95.0, 95.0, 0.0, 599.0, "noaf"),
    ("100K", "noaf"): Fees(149.0, 149.0, 0.0, 699.0, "noaf"),
    ("150K", "noaf"): Fees(229.0, 229.0, 0.0, 829.0, "noaf"),
}
TRADING_DAYS_PER_MONTH = 21

# round-turn commissions + exchange + NFA fees (deducted from Net P&L), per contract
COMMISSION_RT = {"ES": 3.78, "MES": 1.22, "NQ": 3.78, "MNQ": 1.22, "CL": 4.02, "MCL": 1.72, "GC": 4.32, "MGC": 1.92}

# Topstep's published 2025 performance statistics (for calibration / sanity)
PUBLISHED_STATS_2025 = {
    "combines_passed_share": 0.168,
    "participants_funded_at_least_once": 0.518,
    "funded_participants_with_payout": 0.333,
    "xfa_called_up_to_live": 0.0071,
    "lost_combine_on_day_1": 0.63,
}

# ------------------------------------------------------------- Express Funded Account
XFA_MLL = {"50K": 2000.0, "100K": 3000.0, "150K": 4500.0}
XFA_CAP_STANDARD = {"50K": 2000.0, "100K": 3000.0, "150K": 5000.0}
XFA_CAP_STANDARD_DLL = {"50K": 4000.0, "100K": 6000.0, "150K": 10000.0}     # DLL added at Combine checkout
XFA_CAP_CONSISTENCY = {"50K": 3000.0, "100K": 4000.0, "150K": 6000.0}
XFA_CAP_CONSISTENCY_DLL = {"50K": 6000.0, "100K": 8000.0, "150K": 12000.0}
XFA_SCALING = {  # (balance upper bound exclusive, max lots in mini-equivalents)
    "50K": ((1500.0, 2), (2000.0, 3), (float("inf"), 5)),
    "100K": ((1500.0, 3), (2000.0, 4), (3000.0, 5), (float("inf"), 10)),
    "150K": ((1500.0, 3), (2000.0, 4), (3000.0, 5), (4500.0, 10), (float("inf"), 15)),
}
XFA_WIN_THRESHOLD = 150.0
XFA_WINNING_DAYS = 5
XFA_CONSISTENCY_DAYS = 3
XFA_CONSISTENCY_SHARE = 0.40
XFA_MIN_PAYOUT = 125.0
XFA_SPLIT = 0.90
XFA_CAP_SHARE = 0.50
XFA_MAX_ACCOUNTS = 5


def xfa_params(size: str = "50K", path: str = "standard", dll: bool = False) -> dict:
    caps = {("standard", False): XFA_CAP_STANDARD, ("standard", True): XFA_CAP_STANDARD_DLL,
            ("consistency", False): XFA_CAP_CONSISTENCY, ("consistency", True): XFA_CAP_CONSISTENCY_DLL}
    return dict(size=size, mll=XFA_MLL[size], lock_at=0.0, win_threshold=XFA_WIN_THRESHOLD,
                w_required=XFA_WINNING_DAYS if path == "standard" else XFA_CONSISTENCY_DAYS,
                cap_share=XFA_CAP_SHARE, cap_abs=caps[(path, dll)][size], min_payout=XFA_MIN_PAYOUT,
                split=XFA_SPLIT, scaling=XFA_SCALING[size],
                daily_loss_limit=COMBINE_DLL[size] if dll else None,
                consistency_share=XFA_CONSISTENCY_SHARE if path == "consistency" else None,
                path=path)
