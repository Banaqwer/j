"""
Gann Trading Algorithm — Backtesting Engine
=============================================

A complete backtesting framework that validates the W.D. Gann unified trading
algorithm (derived from ALL 18 sources) against historical OHLC price data.

This engine makes the algorithm from gann_trading_algorithm.py fully backtestable
by simulating bar-by-bar trading with:
  - Gann angle support/resistance signals (PDFs 4, 5)
  - Square of 9 confluence detection (PDFs 4, 5, 8)
  - Number vibration (change number) filtering (PDF 6)
  - Volatility-based dynamic level adaptation (PDF 5)
  - Price-Time squaring for cycle alignment (PDF 4)
  - Hexagon Chart cycle timing confirmation (PDF 8)
  - Master Time Period alignment (PDFs 12, 13)
  - Natural 1/8th retracement confluence (PDFs 10, 11, 13)
  - Price-Time Vector harmonics (PDF 9)
  - Gann time counts from pivots (PDFs 7, 11)
  - Lunar cycle awareness (PDF 14)
  - Seasonal date proximity (PDFs 10, 11)
  - 144-cycle and SQ144 levels (PDFs 6, 13)
  - Fibonacci/Lucas retracement confluence (Plummer — Law of Vibration)
  - Squared time cycles from pivots (Jenkins — Secret Science)
  - Spiral calendar Fibonacci timing (Jenkins)
  - Geometric mean equilibrium (Jenkins)
  - Perfect-square price proximity (Jenkins)
  - SQ144 triangle-point proximity (144sqr methodology)
  - Risk management (stop loss, targets, position sizing — PDF 4)

Data Format:
  CSV with columns: date, open, high, low, close, volume (volume optional)
  Date format: YYYY-MM-DD (configurable)

Usage:
------
    from backtest_engine import GannBacktester, BacktestConfig

    config = BacktestConfig(
        initial_capital=100000.0,
        max_risk_pct=10.0,
        min_reward_risk=2.5,
        lookback_bars=10,
    )
    bt = GannBacktester(config)
    result = bt.run("historical_data.csv")
    result.print_summary()
    result.print_trades()
"""

from __future__ import annotations

import csv
import math
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple

from gann_trading_algorithm import GannAnalyzer, TradingSignal


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class BacktestConfig:
    """Configuration for the backtesting engine."""

    # Capital & risk
    initial_capital: float = 100000.0
    max_risk_pct: float = 10.0         # Max % of capital per trade (PDF 4)
    min_reward_risk: float = 2.5       # Minimum reward-to-risk ratio (PDF 4)
    max_position_pct: float = 100.0    # Max position value as % of capital

    # Signal thresholds
    min_confidence: float = 0.25       # Minimum signal confidence to enter
    lookback_bars: int = 10            # Bars of history for volatility calc

    # Exit rules
    use_trailing_stop: bool = True     # Trail stop to breakeven after 50% target
    partial_exit_pct: float = 0.5      # Book 50% at first target (PDF 4 Rule of 72)
    max_hold_bars: int = 72            # Max bars to hold (PDF 4 Rule of 72)

    # Date format
    date_format: str = "%Y-%m-%d"

    # Slippage and commission (per trade, as fraction of price)
    slippage_pct: float = 0.001        # 0.1% slippage
    commission_per_trade: float = 0.0  # Flat commission
    use_fixed_sizing: bool = False     # When True, position sizing uses
    #   initial_capital instead of compounding equity. Useful for highly
    #   volatile assets (e.g. crypto) where compounding leads to
    #   unrealistic exponential growth.


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Bar:
    """A single OHLCV bar."""
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


@dataclass
class Trade:
    """A completed trade record."""
    entry_date: datetime
    exit_date: datetime
    direction: str          # "BUY" or "SELL"
    entry_price: float
    exit_price: float
    stop_loss: float
    target: float
    quantity: float
    pnl: float
    pnl_pct: float
    exit_reason: str        # "target", "stop", "trailing", "timeout", "end"
    confidence: float
    hold_bars: int
    reasons: List[str]


@dataclass
class BacktestResult:
    """Complete backtest results with performance metrics."""
    config: BacktestConfig
    trades: List[Trade]
    equity_curve: List[Tuple[datetime, float]]
    total_bars: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]

    # Performance metrics
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    total_pnl_pct: float = 0.0
    avg_pnl: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    sharpe_ratio: float = 0.0
    final_equity: float = 0.0
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0
    avg_hold_bars: float = 0.0

    def compute_metrics(self) -> None:
        """Calculate all performance metrics from trade list."""
        if not self.trades:
            self.final_equity = self.config.initial_capital
            return

        self.total_trades = len(self.trades)
        self.winning_trades = sum(1 for t in self.trades if t.pnl > 0)
        self.losing_trades = sum(1 for t in self.trades if t.pnl <= 0)
        self.win_rate = (
            self.winning_trades / self.total_trades if self.total_trades > 0 else 0.0
        )

        # PnL
        self.total_pnl = sum(t.pnl for t in self.trades)
        self.total_pnl_pct = (
            self.total_pnl / self.config.initial_capital * 100.0
        )
        self.avg_pnl = (
            self.total_pnl / self.total_trades if self.total_trades > 0 else 0.0
        )

        wins = [t.pnl for t in self.trades if t.pnl > 0]
        losses = [t.pnl for t in self.trades if t.pnl <= 0]
        self.avg_win = sum(wins) / len(wins) if wins else 0.0
        self.avg_loss = sum(losses) / len(losses) if losses else 0.0

        # Profit factor
        gross_profit = sum(wins) if wins else 0.0
        gross_loss = abs(sum(losses)) if losses else 0.0
        self.profit_factor = (
            gross_profit / gross_loss if gross_loss > 0 else 0.0
        )

        # Equity curve and drawdown
        self.final_equity = self.equity_curve[-1][1] if self.equity_curve else self.config.initial_capital
        peak = self.config.initial_capital
        max_dd = 0.0
        max_dd_pct = 0.0
        for _, equity in self.equity_curve:
            if equity > peak:
                peak = equity
            dd = peak - equity
            dd_pct = dd / peak * 100.0 if peak > 0 else 0.0
            if dd > max_dd:
                max_dd = dd
            if dd_pct > max_dd_pct:
                max_dd_pct = dd_pct
        self.max_drawdown = max_dd
        self.max_drawdown_pct = max_dd_pct

        # Sharpe ratio (annualized, assuming daily bars)
        if len(self.trades) > 1:
            returns = [t.pnl_pct for t in self.trades]
            avg_ret = sum(returns) / len(returns)
            var = sum((r - avg_ret) ** 2 for r in returns) / (len(returns) - 1)
            std_ret = math.sqrt(var) if var > 0 else 0.0
            self.sharpe_ratio = (
                avg_ret / std_ret * math.sqrt(252) if std_ret > 0 else 0.0
            )

        # Consecutive wins/losses
        max_cw = 0
        max_cl = 0
        cw = 0
        cl = 0
        for t in self.trades:
            if t.pnl > 0:
                cw += 1
                cl = 0
            else:
                cl += 1
                cw = 0
            max_cw = max(max_cw, cw)
            max_cl = max(max_cl, cl)
        self.max_consecutive_wins = max_cw
        self.max_consecutive_losses = max_cl

        # Average hold
        self.avg_hold_bars = (
            sum(t.hold_bars for t in self.trades) / self.total_trades
            if self.total_trades > 0 else 0.0
        )

    def print_summary(self) -> None:
        """Print a formatted summary of backtest results."""
        print("=" * 78)
        print("GANN ALGORITHM BACKTEST RESULTS")
        print("=" * 78)

        if self.start_date and self.end_date:
            print(f"  Period:            {self.start_date.strftime('%Y-%m-%d')} to "
                  f"{self.end_date.strftime('%Y-%m-%d')}")
        print(f"  Total bars:        {self.total_bars}")
        print(f"  Initial capital:   {self.config.initial_capital:>12,.2f}")
        print(f"  Final equity:      {self.final_equity:>12,.2f}")

        print(f"\n  {'─' * 40}")
        print(f"  Total trades:      {self.total_trades}")
        print(f"  Winning trades:    {self.winning_trades}")
        print(f"  Losing trades:     {self.losing_trades}")
        print(f"  Win rate:          {self.win_rate * 100:.1f}%")

        print(f"\n  {'─' * 40}")
        print(f"  Total PnL:         {self.total_pnl:>12,.2f} ({self.total_pnl_pct:+.2f}%)")
        print(f"  Average PnL:       {self.avg_pnl:>12,.2f}")
        print(f"  Average win:       {self.avg_win:>12,.2f}")
        print(f"  Average loss:      {self.avg_loss:>12,.2f}")
        print(f"  Profit factor:     {self.profit_factor:>12.2f}")

        print(f"\n  {'─' * 40}")
        print(f"  Max drawdown:      {self.max_drawdown:>12,.2f} ({self.max_drawdown_pct:.2f}%)")
        print(f"  Sharpe ratio:      {self.sharpe_ratio:>12.2f}")
        print(f"  Consec. wins:      {self.max_consecutive_wins}")
        print(f"  Consec. losses:    {self.max_consecutive_losses}")
        print(f"  Avg hold (bars):   {self.avg_hold_bars:.1f}")
        print("=" * 78)

    def print_trades(self, max_trades: int = 50) -> None:
        """Print individual trade details."""
        print(f"\n{'─' * 78}")
        print(f"TRADE LOG (showing {min(len(self.trades), max_trades)} of {len(self.trades)})")
        print(f"{'─' * 78}")
        print(f"  {'Date':>12} {'Dir':>5} {'Entry':>10} {'Exit':>10} {'SL':>10} "
              f"{'PnL':>10} {'PnL%':>7} {'Bars':>4} {'Exit Reason':>12} {'Conf':>5}")
        print(f"  {'─' * 12} {'─' * 5} {'─' * 10} {'─' * 10} {'─' * 10} "
              f"{'─' * 10} {'─' * 7} {'─' * 4} {'─' * 12} {'─' * 5}")

        for t in self.trades[:max_trades]:
            print(f"  {t.entry_date.strftime('%Y-%m-%d'):>12} "
                  f"{t.direction:>5} "
                  f"{t.entry_price:>10.2f} "
                  f"{t.exit_price:>10.2f} "
                  f"{t.stop_loss:>10.2f} "
                  f"{t.pnl:>10.2f} "
                  f"{t.pnl_pct:>6.2f}% "
                  f"{t.hold_bars:>4} "
                  f"{t.exit_reason:>12} "
                  f"{t.confidence:>5.2f}")

    def export_csv(self, filepath: str) -> None:
        """Export trade log and equity curve to CSV files."""
        # Trade log
        trade_path = filepath.replace('.csv', '_trades.csv')
        with open(trade_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'entry_date', 'exit_date', 'direction', 'entry_price',
                'exit_price', 'stop_loss', 'target', 'quantity', 'pnl',
                'pnl_pct', 'exit_reason', 'confidence', 'hold_bars', 'reasons',
            ])
            for t in self.trades:
                writer.writerow([
                    t.entry_date.strftime('%Y-%m-%d'),
                    t.exit_date.strftime('%Y-%m-%d'),
                    t.direction, t.entry_price, t.exit_price,
                    t.stop_loss, t.target, t.quantity,
                    round(t.pnl, 2), round(t.pnl_pct, 4),
                    t.exit_reason, t.confidence, t.hold_bars,
                    '; '.join(t.reasons),
                ])

        # Equity curve
        equity_path = filepath.replace('.csv', '_equity.csv')
        with open(equity_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'equity'])
            for dt, eq in self.equity_curve:
                writer.writerow([dt.strftime('%Y-%m-%d'), round(eq, 2)])

        print(f"  Exported trades to: {trade_path}")
        print(f"  Exported equity to: {equity_path}")


# ---------------------------------------------------------------------------
# Position tracking
# ---------------------------------------------------------------------------

@dataclass
class OpenPosition:
    """An open trading position."""
    direction: str
    entry_price: float
    stop_loss: float
    targets: List[float]
    quantity: float
    entry_bar_idx: int
    entry_date: datetime
    confidence: float
    reasons: List[str]
    partial_exited: bool = False
    trailing_stop: Optional[float] = None


# ---------------------------------------------------------------------------
# Backtesting engine
# ---------------------------------------------------------------------------

class GannBacktester:
    """
    Bar-by-bar backtesting engine for the Gann unified algorithm.

    Runs the GannAnalyzer.generate_signal() on each bar using the
    preceding lookback_bars for volatility calculation, then manages
    position entries, exits, and risk per the rules from all PDFs.
    """

    def __init__(self, config: Optional[BacktestConfig] = None):
        self.config = config or BacktestConfig()
        self.analyzer = GannAnalyzer()

    @staticmethod
    def _meets_min_rr(
        target: float, entry: float, risk: float, min_rr: float
    ) -> bool:
        """Check if a target meets the minimum reward-to-risk ratio."""
        if risk <= 0:
            return False
        return abs(target - entry) / risk >= min_rr

    def load_csv(self, filepath: str) -> List[Bar]:
        """
        Load OHLCV data from a CSV file.

        Expected columns: date, open, high, low, close [, volume]
        """
        bars: List[Bar] = []
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    dt = datetime.strptime(
                        row['date'].strip(), self.config.date_format
                    )
                    bar = Bar(
                        date=dt,
                        open=float(row['open']),
                        high=float(row['high']),
                        low=float(row['low']),
                        close=float(row['close']),
                        volume=float(row.get('volume', 0)),
                    )
                    bars.append(bar)
                except (ValueError, KeyError):
                    continue

        bars.sort(key=lambda b: b.date)
        return bars

    def run(self, data_source: str | List[Bar]) -> BacktestResult:
        """
        Run the backtest.

        Parameters
        ----------
        data_source : str or List[Bar]
            Either a filepath to a CSV file, or a list of Bar objects.

        Returns
        -------
        BacktestResult
        """
        if isinstance(data_source, str):
            bars = self.load_csv(data_source)
        else:
            bars = data_source

        if not bars:
            return BacktestResult(
                config=self.config, trades=[], equity_curve=[],
                total_bars=0, start_date=None, end_date=None,
            )

        capital = self.config.initial_capital
        equity_curve: List[Tuple[datetime, float]] = [(bars[0].date, capital)]
        completed_trades: List[Trade] = []
        position: Optional[OpenPosition] = None

        lookback = self.config.lookback_bars

        # Track pivot bar indices for enhanced signal generation
        # (PDFs 8, 9, 11, 12, 13, 14)
        pivot_bar_indices: List[int] = []

        for i, bar in enumerate(bars):
            # --- Detect pivots for enhanced PDF 8-14 analysis ---
            # Simple swing pivot: bar's high is highest or low is lowest
            # in a ±5 bar window (computed only for settled bars)
            pivot_window = 5
            if i >= pivot_window + 1:
                check_idx = i - pivot_window
                if check_idx >= pivot_window:
                    is_swing_high = all(
                        bars[check_idx].high > bars[check_idx + j].high
                        for j in range(-pivot_window, pivot_window + 1)
                        if j != 0 and 0 <= check_idx + j < len(bars)
                    )
                    is_swing_low = all(
                        bars[check_idx].low < bars[check_idx + j].low
                        for j in range(-pivot_window, pivot_window + 1)
                        if j != 0 and 0 <= check_idx + j < len(bars)
                    )
                    if (is_swing_high or is_swing_low) and (
                        not pivot_bar_indices
                        or pivot_bar_indices[-1] != check_idx
                    ):
                        pivot_bar_indices.append(check_idx)
            # ----- CHECK EXITS FIRST -----
            if position is not None:
                exit_price = None
                exit_reason = None
                hold_bars = i - position.entry_bar_idx

                if position.direction == "BUY":
                    # Stop loss hit
                    if bar.low <= position.stop_loss:
                        exit_price = position.stop_loss
                        exit_reason = "stop"
                    # Trailing stop
                    elif (position.trailing_stop is not None and
                          bar.low <= position.trailing_stop):
                        exit_price = position.trailing_stop
                        exit_reason = "trailing"
                    # Target hit
                    elif position.targets and bar.high >= position.targets[0]:
                        if (not position.partial_exited and
                                self.config.partial_exit_pct < 1.0):
                            # Partial exit: book partial_exit_pct at target
                            exit_price = position.targets[0]
                            exit_reason = "partial_target"
                        else:
                            exit_price = position.targets[0]
                            exit_reason = "target"
                    # Timeout
                    elif hold_bars >= self.config.max_hold_bars:
                        exit_price = bar.close
                        exit_reason = "timeout"

                elif position.direction == "SELL":
                    if bar.high >= position.stop_loss:
                        exit_price = position.stop_loss
                        exit_reason = "stop"
                    elif (position.trailing_stop is not None and
                          bar.high >= position.trailing_stop):
                        exit_price = position.trailing_stop
                        exit_reason = "trailing"
                    elif position.targets and bar.low <= position.targets[0]:
                        if (not position.partial_exited and
                                self.config.partial_exit_pct < 1.0):
                            exit_price = position.targets[0]
                            exit_reason = "partial_target"
                        else:
                            exit_price = position.targets[0]
                            exit_reason = "target"
                    elif hold_bars >= self.config.max_hold_bars:
                        exit_price = bar.close
                        exit_reason = "timeout"

                if exit_price is not None and exit_reason is not None:
                    # Apply slippage
                    if position.direction == "BUY":
                        exit_price *= (1 - self.config.slippage_pct)
                    else:
                        exit_price *= (1 + self.config.slippage_pct)

                    if exit_reason == "partial_target":
                        # Partial exit
                        partial_qty = position.quantity * self.config.partial_exit_pct
                        remaining_qty = position.quantity - partial_qty

                        if position.direction == "BUY":
                            pnl = (exit_price - position.entry_price) * partial_qty
                        else:
                            pnl = (position.entry_price - exit_price) * partial_qty

                        pnl -= self.config.commission_per_trade
                        capital += pnl

                        # Update position
                        position.quantity = remaining_qty
                        position.partial_exited = True
                        # Move stop to breakeven (trailing)
                        if self.config.use_trailing_stop:
                            position.trailing_stop = position.entry_price
                        # Move to next target
                        if len(position.targets) > 1:
                            position.targets = position.targets[1:]
                    else:
                        # Full exit
                        qty = position.quantity
                        if position.direction == "BUY":
                            pnl = (exit_price - position.entry_price) * qty
                        else:
                            pnl = (position.entry_price - exit_price) * qty

                        pnl -= self.config.commission_per_trade
                        capital += pnl

                        pnl_pct = (
                            pnl / (position.entry_price * qty) * 100.0
                            if position.entry_price * qty > 0 else 0.0
                        )

                        completed_trades.append(Trade(
                            entry_date=position.entry_date,
                            exit_date=bar.date,
                            direction=position.direction,
                            entry_price=position.entry_price,
                            exit_price=round(exit_price, 4),
                            stop_loss=position.stop_loss,
                            target=position.targets[0] if position.targets else 0,
                            quantity=qty,
                            pnl=round(pnl, 2),
                            pnl_pct=round(pnl_pct, 4),
                            exit_reason=exit_reason,
                            confidence=position.confidence,
                            hold_bars=hold_bars,
                            reasons=position.reasons,
                        ))
                        position = None

            # ----- GENERATE SIGNAL (only if no position) -----
            if position is None and i >= lookback:
                prices_history = [bars[j].close for j in range(i - lookback, i)]
                current_bar = bar

                # Use the lookback-period high/low (swing range) for
                # Gann angle calculations so angles span a meaningful
                # price range rather than a single bar's narrow range.
                lookback_high = max(bars[j].high for j in range(i - lookback, i + 1))
                lookback_low = min(bars[j].low for j in range(i - lookback, i + 1))

                signal = self.analyzer.generate_signal(
                    high=lookback_high,
                    low=lookback_low,
                    current_price=current_bar.close,
                    prices_history=prices_history,
                    account_size=capital,
                    max_risk_pct=self.config.max_risk_pct,
                    bar_index=i,
                    current_date=current_bar.date,
                    pivot_bar_indices=pivot_bar_indices if pivot_bar_indices else None,
                )

                if (signal.direction != "NEUTRAL" and
                        signal.confidence >= self.config.min_confidence and
                        signal.targets):
                    # Find a target that meets minimum R:R requirement.
                    # The signal may provide multiple targets (Gann angles);
                    # also add Square of 9 levels as candidate targets.
                    risk = abs(signal.entry_price - signal.stop_loss)
                    chosen_target = None
                    all_targets = list(signal.targets)

                    # Add SQ9 levels as additional targets
                    for deg, level in signal.sq9_levels.levels.items():
                        if signal.direction == "BUY" and level > signal.entry_price:
                            all_targets.append(level)
                        elif signal.direction == "SELL" and level < signal.entry_price:
                            all_targets.append(level)

                    # Pick the first target that satisfies R:R
                    if signal.direction == "BUY":
                        all_targets.sort()
                    else:
                        all_targets.sort(reverse=True)

                    for tgt in all_targets:
                        if self._meets_min_rr(
                            tgt, signal.entry_price, risk,
                            self.config.min_reward_risk,
                        ):
                            chosen_target = tgt
                            break

                    if chosen_target is not None and risk > 0:
                        # Apply entry slippage
                        entry_price = signal.entry_price
                        if signal.direction == "BUY":
                            entry_price *= (1 + self.config.slippage_pct)
                        else:
                            entry_price *= (1 - self.config.slippage_pct)

                        # Calculate position size
                        sizing_base = (
                            self.config.initial_capital
                            if self.config.use_fixed_sizing
                            else capital
                        )
                        max_risk_amount = sizing_base * self.config.max_risk_pct / 100.0
                        quantity = max_risk_amount / risk if risk > 0 else 0
                        quantity = max(1.0, quantity)

                        # Cap position value to max_position_pct of capital
                        max_pos_value = sizing_base * self.config.max_position_pct / 100.0
                        if quantity * entry_price > max_pos_value and entry_price > 0:
                            quantity = max_pos_value / entry_price

                        capital -= self.config.commission_per_trade

                        position = OpenPosition(
                            direction=signal.direction,
                            entry_price=round(entry_price, 4),
                            stop_loss=signal.stop_loss,
                            targets=[chosen_target] + [
                                t for t in all_targets
                                if t != chosen_target
                                and self._meets_min_rr(
                                    t, entry_price, risk,
                                    self.config.min_reward_risk,
                                )
                            ][:2],
                            quantity=round(quantity, 4),
                            entry_bar_idx=i,
                            entry_date=bar.date,
                            confidence=signal.confidence,
                            reasons=signal.reasons,
                        )

            # Update equity curve
            unrealized = 0.0
            if position is not None:
                if position.direction == "BUY":
                    unrealized = (bar.close - position.entry_price) * position.quantity
                else:
                    unrealized = (position.entry_price - bar.close) * position.quantity
            equity_curve.append((bar.date, capital + unrealized))

        # Close any open position at end
        if position is not None:
            last_bar = bars[-1]
            exit_price = last_bar.close
            hold_bars = len(bars) - 1 - position.entry_bar_idx

            if position.direction == "BUY":
                pnl = (exit_price - position.entry_price) * position.quantity
            else:
                pnl = (position.entry_price - exit_price) * position.quantity

            pnl -= self.config.commission_per_trade
            capital += pnl

            pnl_pct = (
                pnl / (position.entry_price * position.quantity) * 100.0
                if position.entry_price * position.quantity > 0 else 0.0
            )

            completed_trades.append(Trade(
                entry_date=position.entry_date,
                exit_date=last_bar.date,
                direction=position.direction,
                entry_price=position.entry_price,
                exit_price=round(exit_price, 4),
                stop_loss=position.stop_loss,
                target=position.targets[0] if position.targets else 0,
                quantity=position.quantity,
                pnl=round(pnl, 2),
                pnl_pct=round(pnl_pct, 4),
                exit_reason="end",
                confidence=position.confidence,
                hold_bars=hold_bars,
                reasons=position.reasons,
            ))
            equity_curve.append((last_bar.date, capital))

        # Build result
        result = BacktestResult(
            config=self.config,
            trades=completed_trades,
            equity_curve=equity_curve,
            total_bars=len(bars),
            start_date=bars[0].date if bars else None,
            end_date=bars[-1].date if bars else None,
        )
        result.compute_metrics()
        return result


# ---------------------------------------------------------------------------
# Sample data generator for demonstration
# ---------------------------------------------------------------------------

def generate_sample_data(
    start_date: str = "2024-01-02",
    num_bars: int = 252,
    start_price: float = 5000.0,
    daily_vol: float = 0.015,
    date_fmt: str = "%Y-%m-%d",
) -> List[Bar]:
    """
    Generate synthetic OHLC bars for backtesting demonstration.

    Uses a simple random walk with trending and mean-reverting components
    to produce realistic-looking price data.

    Parameters
    ----------
    start_date : str
        Start date string.
    num_bars : int
        Number of bars to generate.
    start_price : float
        Starting close price.
    daily_vol : float
        Daily volatility as fraction (0.015 = 1.5%).
    date_fmt : str
        Date format.

    Returns
    -------
    List[Bar]
    """
    import random
    random.seed(42)  # Reproducible results

    bars: List[Bar] = []
    dt = datetime.strptime(start_date, date_fmt)
    price = start_price

    # Create a cycle pattern (from Gann's cycle theory)
    # Combine a ~30-day cycle and a ~90-day cycle
    for i in range(num_bars):
        # Skip weekends
        while dt.weekday() >= 5:
            dt += timedelta(days=1)

        # Cycle components (simulating Gann cycles)
        cycle_30 = math.sin(2 * math.pi * i / 30) * 0.003
        cycle_90 = math.sin(2 * math.pi * i / 90) * 0.005
        cycle_144 = math.sin(2 * math.pi * i / 144) * 0.002

        # Trend + noise + cycles
        trend = 0.0002  # Slight upward drift
        noise = random.gauss(0, daily_vol)
        ret = trend + noise + cycle_30 + cycle_90 + cycle_144

        price *= (1 + ret)

        # Generate OHLC from close
        intraday_vol = price * daily_vol * 0.5
        high = price + abs(random.gauss(0, intraday_vol))
        low = price - abs(random.gauss(0, intraday_vol))
        open_price = price * (1 + random.gauss(0, daily_vol * 0.3))

        # Ensure OHLC consistency
        high = max(high, open_price, price)
        low = min(low, open_price, price)

        bars.append(Bar(
            date=dt,
            open=round(open_price, 2),
            high=round(high, 2),
            low=round(low, 2),
            close=round(price, 2),
            volume=round(random.uniform(100000, 500000)),
        ))

        # Next trading day
        dt += timedelta(days=1)
        while dt.weekday() >= 5:
            dt += timedelta(days=1)

    return bars


def save_sample_csv(bars: List[Bar], filepath: str) -> None:
    """Save bars to CSV."""
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'open', 'high', 'low', 'close', 'volume'])
        for b in bars:
            writer.writerow([
                b.date.strftime('%Y-%m-%d'),
                b.open, b.high, b.low, b.close, int(b.volume),
            ])


# ---------------------------------------------------------------------------
# Main demonstration
# ---------------------------------------------------------------------------

def main():
    """Run a complete backtesting demonstration."""
    print("=" * 78)
    print("GANN UNIFIED TRADING ALGORITHM — BACKTEST ENGINE")
    print("=" * 78)

    # 1. Generate sample data
    print("\n1. Generating sample OHLC data (252 bars, ~1 year)...")
    bars = generate_sample_data(
        start_date="2024-01-02",
        num_bars=252,
        start_price=5000.0,
        daily_vol=0.015,
    )
    print(f"   Generated {len(bars)} bars from {bars[0].date.strftime('%Y-%m-%d')} "
          f"to {bars[-1].date.strftime('%Y-%m-%d')}")
    print(f"   Price range: {min(b.low for b in bars):.2f} - {max(b.high for b in bars):.2f}")

    # Save sample CSV
    sample_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "sample_data.csv")
    save_sample_csv(bars, sample_csv)
    print(f"   Saved to: {sample_csv}")

    # 2. Configure backtester
    print("\n2. Configuring backtester...")
    config = BacktestConfig(
        initial_capital=100000.0,
        max_risk_pct=10.0,
        min_reward_risk=2.5,
        min_confidence=0.25,
        lookback_bars=10,
        max_hold_bars=72,
        use_trailing_stop=True,
        partial_exit_pct=0.5,
        slippage_pct=0.001,
    )
    print(f"   Initial capital:  {config.initial_capital:,.0f}")
    print(f"   Max risk/trade:   {config.max_risk_pct}%")
    print(f"   Min R:R ratio:    {config.min_reward_risk}:1")
    print(f"   Min confidence:   {config.min_confidence}")
    print(f"   Lookback bars:    {config.lookback_bars}")
    print(f"   Max hold bars:    {config.max_hold_bars}")

    # 3. Run backtest
    print("\n3. Running backtest...")
    bt = GannBacktester(config)
    result = bt.run(bars)

    # 4. Display results
    print()
    result.print_summary()
    result.print_trades(max_trades=20)

    # 5. Export results
    export_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "backtest_results.csv")
    print(f"\n5. Exporting results...")
    result.export_csv(export_path)

    # 6. Demonstrate CSV loading
    print(f"\n6. Demonstrating CSV file loading...")
    print(f"   You can run your own backtest with:")
    print(f"   >>> from backtest_engine import GannBacktester, BacktestConfig")
    print(f"   >>> bt = GannBacktester(BacktestConfig(initial_capital=100000))")
    print(f"   >>> result = bt.run('your_data.csv')  # CSV with date,open,high,low,close")
    print(f"   >>> result.print_summary()")
    print(f"   >>> result.export_csv('output.csv')")

    print(f"\n{'=' * 78}")
    print("Backtest demonstration complete.")
    print(f"{'=' * 78}")


if __name__ == "__main__":
    main()
