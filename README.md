# Portfolio Risk Analyzer

Interactive web application for analyzing investment portfolio performance and risk metrics using real-time market data.

## Overview

Built this to learn how to work with Python libraries and apply my coursework to something practical. 

## Features

**Risk Metrics**
- Sharpe Ratio: risk-adjusted return calculation
- CAGR: compound annual growth rate
- Maximum Drawdown: worst peak-to-valley decline analysis

**Analysis Tools**
- Real-time stock data via Yahoo Finance API
- Benchmark comparison against market indices (SPY, QQQ, etc.)
- Interactive visualizations of returns and drawdowns
- Downloadable HTML tear sheets with detailed metrics

**User Experience**
- Input validation with helpful error messages
- Hover tooltips explaining financial terms
- Custom portfolio weighting
- Flexible date range selection

## Tech Stack

- Python
- Streamlit (web framework)
- QuantStats (financial metrics)
- yfinance (market data)
- Pandas (data processing)
- Matplotlib/Seaborn (visualization)

## Installation

Clone the repository:
```bash
git clone https://github.com/chillbeaverdev/portfolio-risk-analyzer.git
cd portfolio-risk-analyzer
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
streamlit run portfolio_analyzer.py
```

Your browser will automatically open to `http://localhost:8501`

**Steps:**
1. Enter stock tickers separated by commas (e.g., AAPL, MSFT, GOOGL)
2. Enter portfolio weights that sum to 1.0 (e.g., 0.25, 0.25, 0.25, 0.25 for equal weighting)
3. Choose a benchmark ticker to compare against (SPY for S&P 500, QQQ for NASDAQ)
4. Select your date range for analysis
5. Click "Analyze Portfolio"
6. View metrics and download the full tear sheet report

## Why I Built This

Wanted to understand how Python libraries work together in a real application rather than just following tutorials. 
Wanted to demystify investing and make portfolio analysis less overwhelming by breaking down the key metrics in a simple interface.
## Future Improvements

- AI chatbot for explaining metrics in plain language
- Stress testing scenarios with what-if analysis
- Quick portfolio health snapshot/summary view
- Historical comparison showing how portfolio would have performed in past market crashes
- Sector allocation breakdown and diversification scoring

## Technical Notes

Uses equal-weighted portfolios by default but supports custom allocations. All calculations follow standard financial formulas. Sharpe ratio assumes risk-free rate of 0 for simplicity.

Data pulled from Yahoo Finance may have gaps or errors for certain tickers or date ranges. Tool includes validation to catch common input mistakes.
