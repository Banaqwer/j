# Source Files Used as Basis for the Trading Algorithm

This document lists **every file** in the repository that was used as the basis
for building and backtesting the W.D. Gann unified trading algorithm.

---

## 1. Gann PDF Documents (14 files — knowledge basis)

These PDFs were read line by line and their teachings were extracted,
cross-referenced, and merged into the algorithm's signal generation logic.

| # | Filename | Title / Subject |
|---|----------|-----------------|
| 1 | `321139539-20-Years-of-Studying-Gann.pdf` | "20 Years of Studying Gann" — Cycles of repetition, Law of Vibration, numerology, time cycles, ~10% inversion rate, vibrational trading ranges |
| 2 | `344593197-Walker-Myles-Wilson-Super-Timing-W-D-Ganns-Astrological-Method-pdf.pdf` | "Super Timing — W.D. Gann's Astrological Method" by Walker Myles Wilson — Planetary conjunctions, squares, oppositions, trines; heliocentric & geocentric timing |
| 3 | `512911483-WD-Gann-Astro-Cycles.pdf` | "WD Gann Astro Cycles" — Planetary cycle-based market timing charts and overlays |
| 4 | `676102941-Gann.pdf` | "Gann through My Lens" by Raju Chowksey — Square of 9, price-time squaring (P = T²), SAP, 2B/2T patterns, ATM trade rules, Rule of 72 |
| 5 | `81180859-Intraday-Trade-Using-Gann-Angle.pdf` | "Intraday Trade Using Gann Angle" by Soumya Ranjan Panda — 11 Gann angle trend lines, degree factors, volatility-based dynamic SQ9/SQ12, trend confirmation |
| 6 | `96954586-WD-GANN-Number-Vibrations.pdf` | "WD GANN Number Vibrations" — Numerology digit reduction, 144-cycle, 360° circle divisions, 3-6-9 symmetry |
| 7 | `tunnelthruairorl00gann.pdf` | "Tunnel Thru the Air" by W.D. Gann — Foundational novel encoding cycle lengths (30/36/45/60/90/120/144/180/225/360 days), time dominance, "wheel within a wheel" |
| 8 | `293714302-1931-Usage-of-Gann-SQ9-Hexagon-Chart.pdf` | "1931 Usage of Gann SQ9 Hexagon Chart" — Hexagon Chart structure (1→7→19→37→61→91→127…), 90° crosses, 30-year cube cycle, 66-month campaigns |
| 9 | `351158936-TS-VECTOR-2.pdf` | "TS-VECTOR-2" by Tarasov — Price-Time Vector (√(ΔPrice² + ΔTime²)), key distances at 180/360/720/1080°, equidistant ellipses |
| 10 | `362311634-Gann-s-Master-Mathematical-Formula-for-Market-Predictions.pdf` | "Gann's Master Mathematical Formula for Market Predictions" by Ferrera — Square of 52/90/144 overlays, natural 1/8th price divisions, seasonal timing |
| 11 | `402779044-Understanding-Gann-Price-and-Time-Cycle-docx.pdf` | "Understanding Gann Price and Time Cycle" — 1/8th divisions of range and time, 30-year cycle, time counts (30/45/60/90…360 days), 1/2 center of gravity |
| 12 | `411614909-Gann-s-Master-Time-Factor-Flanagan.pdf` | "Gann's Master Time Factor" by Flanagan — Master Time Factor, annual forecast, Gann's 12-item pre-trade checklist |
| 13 | `623199454-1953-Mathematical-Formula-for-Market-Predictions.pdf` | "1953 Mathematical Formula for Market Predictions" by W.D. Gann — Square of 144 (GREAT SQUARE), Master Numbers 3/5/7/9/12, 20,736 Great Cycle |
| 14 | `550659259-A-Moon-Beam-Thru-the-Tunnel-by-Petter-Ivar-Amundsen.pdf` | "A Moon Beam Thru the Tunnel" by Petter Ivar Amundsen — Lunar Return decoded from Tunnel, ~29.5-day lunar cycle, Venus-Mars conjunction timing |

---

## 2. Extracted Text (1 file — decoded from PDF 7)

| Filename | Description |
|----------|-------------|
| `tunnel_extracted.txt` | Full text extraction of "Tunnel Thru the Air" (PDF 7) used by `tunnel_decoder.py` to extract dates, cycles, and encoded trading knowledge |

---

## 3. Bitcoin Market Data (60 files — backtesting data)

Binance BTCUSDT daily kline (candlestick) data covering January 2021 through
December 2025 (5 full years). Each zip file contains one month of daily OHLCV
data used for the 5-year backtest.

| Filename | Period |
|----------|--------|
| `BTCUSDT-1d-2021-01.zip` | January 2021 |
| `BTCUSDT-1d-2021-02.zip` | February 2021 |
| `BTCUSDT-1d-2021-03.zip` | March 2021 |
| `BTCUSDT-1d-2021-04.zip` | April 2021 |
| `BTCUSDT-1d-2021-05.zip` | May 2021 |
| `BTCUSDT-1d-2021-06.zip` | June 2021 |
| `BTCUSDT-1d-2021-07.zip` | July 2021 |
| `BTCUSDT-1d-2021-08.zip` | August 2021 |
| `BTCUSDT-1d-2021-09.zip` | September 2021 |
| `BTCUSDT-1d-2021-10.zip` | October 2021 |
| `BTCUSDT-1d-2021-11.zip` | November 2021 |
| `BTCUSDT-1d-2021-12.zip` | December 2021 |
| `BTCUSDT-1d-2022-01.zip` | January 2022 |
| `BTCUSDT-1d-2022-02.zip` | February 2022 |
| `BTCUSDT-1d-2022-03.zip` | March 2022 |
| `BTCUSDT-1d-2022-04.zip` | April 2022 |
| `BTCUSDT-1d-2022-05.zip` | May 2022 |
| `BTCUSDT-1d-2022-06.zip` | June 2022 |
| `BTCUSDT-1d-2022-07.zip` | July 2022 |
| `BTCUSDT-1d-2022-08.zip` | August 2022 |
| `BTCUSDT-1d-2022-09.zip` | September 2022 |
| `BTCUSDT-1d-2022-10.zip` | October 2022 |
| `BTCUSDT-1d-2022-11.zip` | November 2022 |
| `BTCUSDT-1d-2022-12.zip` | December 2022 |
| `BTCUSDT-1d-2023-01.zip` | January 2023 |
| `BTCUSDT-1d-2023-02.zip` | February 2023 |
| `BTCUSDT-1d-2023-03.zip` | March 2023 |
| `BTCUSDT-1d-2023-04.zip` | April 2023 |
| `BTCUSDT-1d-2023-05.zip` | May 2023 |
| `BTCUSDT-1d-2023-06.zip` | June 2023 |
| `BTCUSDT-1d-2023-07.zip` | July 2023 |
| `BTCUSDT-1d-2023-08.zip` | August 2023 |
| `BTCUSDT-1d-2023-09.zip` | September 2023 |
| `BTCUSDT-1d-2023-10.zip` | October 2023 |
| `BTCUSDT-1d-2023-11.zip` | November 2023 |
| `BTCUSDT-1d-2023-12.zip` | December 2023 |
| `BTCUSDT-1d-2024-01.zip` | January 2024 |
| `BTCUSDT-1d-2024-02.zip` | February 2024 |
| `BTCUSDT-1d-2024-03.zip` | March 2024 |
| `BTCUSDT-1d-2024-04.zip` | April 2024 |
| `BTCUSDT-1d-2024-05.zip` | May 2024 |
| `BTCUSDT-1d-2024-06.zip` | June 2024 |
| `BTCUSDT-1d-2024-07.zip` | July 2024 |
| `BTCUSDT-1d-2024-08.zip` | August 2024 |
| `BTCUSDT-1d-2024-09.zip` | September 2024 |
| `BTCUSDT-1d-2024-10.zip` | October 2024 |
| `BTCUSDT-1d-2024-11.zip` | November 2024 |
| `BTCUSDT-1d-2024-12.zip` | December 2024 |
| `BTCUSDT-1d-2025-01.zip` | January 2025 |
| `BTCUSDT-1d-2025-02.zip` | February 2025 |
| `BTCUSDT-1d-2025-03.zip` | March 2025 |
| `BTCUSDT-1d-2025-04.zip` | April 2025 |
| `BTCUSDT-1d-2025-05.zip` | May 2025 |
| `BTCUSDT-1d-2025-06.zip` | June 2025 |
| `BTCUSDT-1d-2025-07.zip` | July 2025 |
| `BTCUSDT-1d-2025-08.zip` | August 2025 |
| `BTCUSDT-1d-2025-09.zip` | September 2025 |
| `BTCUSDT-1d-2025-10.zip` | October 2025 |
| `BTCUSDT-1d-2025-11.zip` | November 2025 |
| `BTCUSDT-1d-2025-12.zip` | December 2025 |

---

## Summary

| Category | File Count | Purpose |
|----------|-----------|---------|
| Gann PDF documents | 14 | Knowledge basis — all trading concepts extracted from these |
| Extracted text | 1 | Decoded content from "Tunnel Thru the Air" |
| Bitcoin market data | 60 | 5-year daily OHLCV data for backtesting (2021–2025) |
| **Total source files** | **75** | |
