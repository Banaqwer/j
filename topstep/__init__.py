"""topstep: probability, dynamic programming and Monte Carlo tools for the
Topstep Trading Combine / Express Funded Account decision problem.

Modules
-------
rules        : dataclasses holding every rule parameter (sizes, targets, MLL, payouts ...)
closed_form  : analytic hitting probabilities (gambler's ruin, trailing drawdown, Topstep lock)
edge         : trader edge models (per-trade win rate / R-multiple -> drift, variance, gamma)
dp_combine   : exact optimal daily policy for the Combine by value iteration
dp_funded    : optimal trade / payout policy for the funded account by value iteration
sim          : trade-level Monte Carlo of the whole pipeline (Combine -> XFA -> payouts)
"""
__all__ = ["rules", "closed_form", "edge", "dp_combine", "dp_funded", "sim"]
