# SPEC

C1) Scope & alignment (LOCKED)
- Instrument: SPY daily.
- Timezone: America/New_York.
- Feature timestamp: 16:00 ET for trading day t.
- Trading rule: decisions based on features at t execute at next open (t+1).
- All training/feature computation uses only information available up to t.

C2) Bodies (LOCKED)
Included: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune.
Excluded: Pluto.

C3) Circular math (LOCKED formulas)
wrap360(x) = x mod 360 mapped to [0,360).
circ_dist(a,b) = min(|a-b|, 360-|a-b|).
All angle diffs computed in degrees then converted to radians as needed.

C4) Pair relative speed (LOCKED)
For pair (i,j):
Δ_ij(t)=circ_dist(λ_i,λ_j)
Compute unwrapped signed difference in radians u_ij(t)=unwrap(radians(λ_i-λ_j)).
Relative angular speed: dΔ_rel(t) = |u_ij(t)-u_ij(t-1)| in rad/day (convert to deg/day if needed).

C5) Aspect set (LOCKED)
Aspects A (deg): {0,30,45,60,90,120,135,150,180}

C6) Orb logic (UPGRADED: speed-based window, not fixed)
Orb degrees baseline by fastest body (as earlier):
Moon 1.25; Mercury 1.50; Venus 1.50; Mars 2.00; Jupiter 2.50; Saturn 2.50; Uranus 3.00; Neptune 3.00; Sun 2.00 when fastest.
BUT for timing influence you must convert orb into a TIME WINDOW using relative speed:
W_aspect_ij(t) = max(1, ceil( orb_deg_ij / (|dΔ_rel_deg_per_day(t)| + 1e-6) ))
This replaces crude ±N day windows.

C7) von Mises kernel (LOCKED) + κ derivation
θ = radians(Δ - A)
prox = exp(κ cos(θ)) / exp(κ)
κ derived from orb boundary prox(orb)/prox(0)=0.5:
κ = ln(0.5) / (cos(radians(orb_deg)) - 1)

C8) Aspect time kernel (LOCKED, continuous)
Encode both angular proximity and time proximity:
K_angle = prox (above)
K_time = exp( -(d_t^2)/(2*W_aspect_ij(t)^2) ) where d_t = signed trading-day distance to nearest exact-aspect timestamp for that pair/aspect (computed by continuous-time event solving).
Define combined:
K_aspect = K_angle * K_time
Also include signed versions using approach/separate sign.

C9) Continuous-time event solving (LOCKED)
You must not rely on daily sampling to find event times.
For each event type (new/full, node crossing, station, exact aspect crossing), do:
1) evaluate the relevant function on an HOURLY grid in UTC:
   - new: g(t)=wrap_to_pi(ε(t) - 0)
   - full: g(t)=wrap_to_pi(ε(t) - π)
   - node: g(t)=β_moon(t)
   - station: g(t)=dλ_planet(t)
   - exact aspect: g(t)=wrap_to_pi( (λ_i-λ_j)(t) - A )
2) find sign changes / brackets
3) refine with bracketed bisection (not quadratic) to tolerance 1 minute
4) store exact event_time_utc and aligned event_date (nearest trading day)
This ensures maximum accuracy.

C10) Ephemeris source & frames (LOCKED)
Use JPL kernels via SPICE:
- de440s.bsp
- naif0012.tls
- pck00010.tpc
Lock SPICE settings:
- frame: J2000
- output: geocentric apparent ecliptic longitude/latitude (state in J2000 then rotate to ecliptic)
- correction flags: NONE (no light-time) for determinism, OR explicitly LT+S if you choose; YOU MUST LOCK ONE AND USE IT CONSISTENTLY.
Choose: correction="NONE" for this project.

Compute at 16:00 ET (converted to UTC) for each trading day:
λ, β, r, RA, Dec, dλ, ddλ, dDec
Unwrap longitudes in radians before differencing.

C11) Moon extras (LOCKED)
Compute elongation ε(t) using Sun/Moon vectors.
phase=(1-cos ε)/2
Compute event times by continuous-time solving above.
Compute adaptive windows W_event(t)=max(1, ceil( τ/|dx/dt| )) where τ is tolerance specific to variable:
τ_ε=2.0°; τ_β=0.5°; τ_dec=0.5°; τ_r=0.002 AU
Kernel:
K_event(t)=exp(-(d^2)/(2*W_event^2))
Store signed distance, abs distance, window, kernel, kernel_signed.

C12) Swiss validation (LOCKED)
Random N=200 trading dates, compute λ via Swiss at same UTC time.
Tolerance:
Moon/Mercury/Venus <=0.02°, others <=0.05°. Hard fail if exceeded.
CI smoke N=5.

C13) Features (LOCKED blocks A..K plus upgrades)
Block A Controls:
- DOW, month, end-of-month flag, quarter-end flag, turn-of-year flag
- RV20, ATR14, MA20 slope, vol z-score 252
- OPEX week flag (3rd Friday of month) and FOMC/CPI flags only if provided via macro file; if absent, keep as zeros but keep schema

Block B Lunar:
- elongation sin/cos harmonics 1..16
- phase, dphase
- event kernels for new/full/node/perigee/apogee/dec extremes using adaptive windows (no fixed ±2)
- declination cycle harmonics 1..16

Blocks C/D/E Planet cycles:
- raw states + derivatives
- harmonic sin/cos for k=1..H_body

Block F Aspects:
- for all unordered pairs and all aspects:
  K_aspect = K_angle*K_time
  approach/separate sign, hit flags as diagnostic only
  phase features: sin(Δ-A), cos(Δ-A) (signed phase)
- event times for exact aspects computed continuously and used for K_time

Block G Retrograde/stations:
- retro flag: dλ<0
- station events solved in continuous time (dλ crosses 0) + adaptive kernel windows based on |ddλ|
- station kernel features

Block H Confluence (pairwise + higher-order):
- E_all, E_inner, E_outer, E_cross using top-k=10 on K_aspect values
- entropy and derivatives
- cancellation: E_sup, E_ten, E_net, E_ratio, conflict_index using K_aspect grouped by aspect sets
- higher-order confluence:
  * triad_confluence: count and energy when 3 specific aspects across 3 bodies align within same day (define as sum of top 3 pairwise K_aspect among triad)
  * quartet_confluence similarly for 4 bodies
  Implement generic higher-order measure: for each day, take top M=20 aspects, compute clustering coefficient of involved bodies, output cluster_energy and cluster_size.

Block I Transforms:
- delta harmonics for key deltas as before
- wavelets: PyWavelets CWT with Morlet ω0=6, scales list locked; normalize power = |coeff|^2 / scale; ignore COI edges by flagging or excluding last/first 10 days in ridge slope computation.
- FFT features locked (as before)
- Kalman locked (as earlier) applied on E_all-related vector (with dE defined as simple diff)
- multi-resolution: compute weekly aggregated E_all and event kernels (5-day rolling sum) and include both daily and weekly features.

Block J DTW locked:
- z-normalize each 252 window
- distance metric L2
- band 20%
- output best lag, best dist, and lag stability (rolling std of best lag over 63 days)

Block K Learned kernel:
- Input selection locked: top 300 aspect features by mutual information on train + confluence energies + event kernels + FFT top amps/phases
- MLP architecture locked: input->128 GELU->drop0.1->128 GELU->drop0.1->out
- optimizer AdamW lr=1e-3 wd=1e-4, batch=1024, epochs=20, early stop patience=5 on val logloss
- outputs calibrated probs via Platt scaling train-only

C14) Labels (LOCKED + expanded)
Direction classification: y_dir_h for h in {1,3,5,10,21} using adj_close log returns.
Vol event: y_vol_h for h in {5,10} using forward realized vol vs expanding 90th percentile train-only.
Tail: y_tail on forward 10d return vs expanding 5th percentile.
Pivot definitions (TWO required):
- Zigzag confirmation pivot (ATR-based, min_sep=5)
- Fractal pivot (Bill Williams style: high higher than prior 2 and next 2; confirm with 2-bar delay)
Create y_pivot_zigzag, y_pivot_fractal.
Timing label explicitly required:
- y_timing = 1 if (pivot or vol event or tail) occurs within next 5 days else 0.

C15) Modeling (LOCKED + expanded)
CV: purged walk-forward outer (train 5y test 6m step 3m embargo 21d)
Nested tuning: inner purged splits on train only.
Fold-safe preprocessing: standardize features using train-only mean/std; apply same transform to test.

Model families required:
1) ElasticNet logistic (grid fixed)
2) LightGBM (grid fixed + lock base settings: objective=binary, metric=binary_logloss, boosting=gbdt, num_boost_round=2000, early_stopping_rounds=100, feature_fraction/subsample as in grid)
3) RandomForest (grid fixed)
4) TCN locked architecture (seq_len=60, kernel=3, blocks=3, dilations [1,2,4], AdamW lr=1e-3, max_epochs=50, patience=7)
5) GAM cyclic spline model on angular features (cyclic splines for λ and Δ phases) for interpretability baseline.

Seeds: {11,23,37,51,89} bagging for each model -> mean probs + var_seeds.

Stacking locked:
- inner OOF for stacker uses sequential time folds (5 splits) with embargo; no random CV.
- stacker = logistic regression; trained only on OOF predictions.
Calibration:
- isotonic if train N>=5000 else Platt, train-only.

Meta-labeling locked:
Primary trigger: p_timing>=0.60 and |dir_score|>=0.15
Meta model predicts correctness. p_meta used in sizing.
No-trade zone:
- if var_seeds > 0.02 OR conformal uncertainty above threshold -> signal forced to 0.

Conformal calibration:
- implement split conformal on train to get uncertainty bands for p_dir; export uncertainty as feature and gating rule.

Regime detection locked:
HMM locked as earlier; additionally allow regime probabilities as features but sizing multiplier remains locked.

Cost-aware selection:
Objective remains logloss, but add turnover penalty in tie-break: if turnover differs by >20%, prefer lower turnover.

C16) Backtest & risk overlays (LOCKED + expanded)
Base rules as earlier (next open, slippage, stop/TP/trailing/time stop, gap rules, worst-case same bar).
Add volatility targeting overlay:
- target_vol = 10% annualized; position size scaled by target_vol / (RV20*sqrt(252)) capped [0.2, 1.5]
Add drawdown risk-off:
- if rolling peak-to-trough drawdown > 12%, reduce max size by 50% until drawdown < 8%.
Add regime exposure caps:
- regime2 (high vol): max size multiplier 0.6 (already), and max gross exposure capped at 0.5.

C17) Statistical validation (LOCKED + expanded)
- Placebos: circular shift, phase randomization (confluence-only), planet shuffle (full recompute) B=200 each.
- Add calendar placebo: shuffle calendar blocks (permute months within years) to test seasonality confound.
- RC/SPA candidate universe expanded:
  include model family variants as well as risk configs, but cap deterministically at 200.
- Stationary bootstrap locked (Politis–Romano centered returns) B=2000 L=10.
- Add PSR/DSR: compute Probabilistic Sharpe and Deflated Sharpe.
- Add feature stability reporting: Jaccard overlap of selected features across folds; require minimum overlap threshold 0.15 else warn in report.
- Add prequential evaluation: rolling train->trade->advance simulation separate from CV.

C18) QuantConnect integration (LOCKED + expanded)
- local data parity must use LEAN-exported adjusted bars, not Stooq/yfinance.
- predictions file includes version + SHA256 checksum in header; QC verifies.
- QC uses ObjectStore key "predictions/preds_spy_daily.csv"
- QC schedule: AfterMarketOpen("SPY",1)
- QC stop/TP uses StopMarket and Limit orders; enforce worst-case by manual liquidation priority if both touched.

C19) Reporting (LOCKED + expanded)
Report must include:
- ephemeris validation summary + max/mean error
- leakage checks summary
- feature drift plots
- adversarial AUC over time
- calibration plots by subperiod and by regime
- placebo performance distributions with p-values
- RC/SPA p-values
- PSR/DSR
- block attribution A..K + higher-order block contributions
- prequential results vs CV results
- parity test results
