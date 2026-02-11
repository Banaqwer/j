<#
.SYNOPSIS
    Download Ethereum (ETH/USDT) daily kline data from the Binance API.

.DESCRIPTION
    Downloads ETHUSDT 1-day kline (candlestick) data from the Binance public
    API and saves each month as a zip file containing a CSV, matching the
    same format used for the BTCUSDT data already in this repository.

    The Binance klines endpoint returns data in this CSV column order:
        open_time, open, high, low, close, volume, close_time,
        quote_volume, count, taker_buy_base, taker_buy_quote, ignore

    No API key is required — this uses the public /api/v3/klines endpoint.

.PARAMETER Symbol
    Trading pair symbol (default: ETHUSDT).

.PARAMETER Interval
    Kline interval (default: 1d for daily).

.PARAMETER StartYear
    First year to download (default: 2021).

.PARAMETER EndYear
    Last year to download (default: current year).

.PARAMETER OutputDir
    Directory to save the zip files (default: current directory).

.EXAMPLE
    .\download_eth_data.ps1

    Downloads ETHUSDT daily data from Jan 2021 to present, saving
    monthly zip files like ETHUSDT-1d-2021-01.zip in the current directory.

.EXAMPLE
    .\download_eth_data.ps1 -StartYear 2022 -EndYear 2024

    Downloads only 2022-2024 data.

.EXAMPLE
    .\download_eth_data.ps1 -Symbol SOLUSDT -OutputDir .\solana_data

    Downloads Solana daily data instead of Ethereum.

.NOTES
    Binance API rate limit: 1200 requests per minute (we use ~60 requests
    total for 5 years of monthly data, well within limits).
    No API key required for public market data endpoints.
#>

[CmdletBinding()]
param(
    [string]$Symbol = "ETHUSDT",
    [string]$Interval = "1d",
    [int]$StartYear = 2021,
    [int]$EndYear = (Get-Date).Year,
    [string]$OutputDir = "."
)

# Binance public API base URL
$BaseUrl = "https://api.binance.com/api/v3/klines"

# Ensure output directory exists
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

Write-Host "============================================================"
Write-Host "  Binance $Symbol Daily Kline Downloader (PowerShell)"
Write-Host "============================================================"
Write-Host ""
Write-Host "  Symbol:     $Symbol"
Write-Host "  Interval:   $Interval"
Write-Host "  Period:     $StartYear-01 to $EndYear-12"
Write-Host "  Output:     $OutputDir"
Write-Host ""

$totalFiles = 0
$totalBars = 0

for ($year = $StartYear; $year -le $EndYear; $year++) {
    for ($month = 1; $month -le 12; $month++) {

        # Calculate start and end timestamps for this month
        $startDate = Get-Date -Year $year -Month $month -Day 1 -Hour 0 -Minute 0 -Second 0
        if ($month -eq 12) {
            $endDate = Get-Date -Year ($year + 1) -Month 1 -Day 1 -Hour 0 -Minute 0 -Second 0
        } else {
            $endDate = Get-Date -Year $year -Month ($month + 1) -Day 1 -Hour 0 -Minute 0 -Second 0
        }

        # Skip future months
        if ($startDate -gt (Get-Date)) {
            continue
        }

        # Convert to Unix milliseconds
        $startMs = [long]([DateTimeOffset]$startDate).ToUnixTimeMilliseconds()
        $endMs   = [long]([DateTimeOffset]$endDate).ToUnixTimeMilliseconds() - 1

        $monthStr = $month.ToString("D2")
        $csvName  = "$Symbol-$Interval-$year-$monthStr.csv"
        $zipName  = "$Symbol-$Interval-$year-$monthStr.zip"
        $zipPath  = Join-Path $OutputDir $zipName
        $csvPath  = Join-Path $OutputDir $csvName

        Write-Host -NoNewline "  Downloading $year-$monthStr ... "

        # Build the API URL
        $url = "${BaseUrl}?symbol=${Symbol}&interval=${Interval}&startTime=${startMs}&endTime=${endMs}&limit=1000"

        try {
            # Call the Binance API
            $response = Invoke-RestMethod -Uri $url -Method Get -ErrorAction Stop

            if ($response.Count -eq 0) {
                Write-Host "no data (skipped)"
                continue
            }

            # Write CSV (no header — matches Binance zip format)
            $csvLines = @()
            foreach ($kline in $response) {
                $csvLines += ($kline -join ",")
            }
            $csvLines | Out-File -FilePath $csvPath -Encoding UTF8 -Force

            # Create zip file containing the CSV
            Compress-Archive -Path $csvPath -DestinationPath $zipPath -Force

            # Remove the temporary CSV (keep only the zip)
            Remove-Item $csvPath -Force

            $barCount = $response.Count
            $totalBars += $barCount
            $totalFiles++

            Write-Host "$barCount bars -> $zipName"

        } catch {
            Write-Host "ERROR: $($_.Exception.Message)"
        }

        # Small delay to respect rate limits
        Start-Sleep -Milliseconds 250
    }
}

Write-Host ""
Write-Host "============================================================"
Write-Host "  Download complete!"
Write-Host "  Files created: $totalFiles"
Write-Host "  Total bars:    $totalBars"
Write-Host "  Output dir:    $OutputDir"
Write-Host "============================================================"
Write-Host ""
Write-Host "To backtest with this data, run:"
Write-Host "  python backtest_ethereum_weekly.py"
Write-Host ""
Write-Host "Or load the data in Python (adapt the BTC loader for ETH):"
Write-Host "  # See backtest_bitcoin_real.py load_binance_btc_data() for"
Write-Host "  # how to parse the zip files — change the glob to ETHUSDT-1d-*.zip"
