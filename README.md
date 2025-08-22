# StockTracker: Interactive Stock & Portfolio Dashboard

StockTracker is an interactive Python dashboard built with Streamlit. It allows users to analyze individual stocks, track portfolio performance, and explore key financial metrics such as Moving Averages, RSI, Sharpe Ratio, and Max Drawdown.

## Features

- Multi-stock selection by full company names
- Line charts & candlestick charts with **MA20 and MA50**
- Metrics Insights:
  - **MA20 (20-day moving average):** Average closing price of the last 20 trading days. Short-term trend indicator.
  - **MA50 (50-day moving average):** Average closing price of the last 50 trading days. Medium-term trend indicator.
  - **RSI (Relative Strength Index):** Measures the speed and change of price movements. Values above 70 indicate overbought; below 30 indicate oversold. Calculated as: `RSI = 100 - (100 / (1 + RS))`, where RS = average gain / average loss over 14 periods.
  - **Sharpe Ratio:** Risk-adjusted return metric. Calculated as the mean daily return divided by standard deviation of daily returns, annualized: `Sharpe = (mean return / std return) * sqrt(252)`.
  - **Max Drawdown:** Largest peak-to-trough decline in cumulative returns over the period, representing maximum potential loss.
- Portfolio view with weighted stock contributions
- Interactive sidebar to adjust:
  - Time period
  - Chart type (line/candlestick)
  - Moving average windows
  - Metrics display
  - Portfolio stocks and weights

## Installation

1. Clone the repository:

```bash
git clone https://github.com/pharquissandas/StockTracker.git
cd StockTracker
