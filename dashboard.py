import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page Setup #
st.set_page_config(page_title="StockTracker", layout="wide")
st.title("StockTracker: Interactive Stock & Portfolio Dashboard")
st.markdown(
    "Welcome! Analyze your favorite stocks and track your portfolio performance in one place."
)

# Stock Options #
stock_options = {
    "Apple Inc.": "AAPL",
    "Microsoft Corporation": "MSFT",
    "Tesla, Inc.": "TSLA",
    "Amazon.com, Inc.": "AMZN",
    "Alphabet Inc. (Google)": "GOOGL",
    "NVIDIA Corporation": "NVDA",
    "Meta Platforms, Inc.": "META"
}

# Sidebar #
st.sidebar.header("Dashboard Controls")

# Stock selection
st.sidebar.subheader("Stock Selection")
selected_stock_names = st.sidebar.multiselect(
    "Select the stocks to analyze:", 
    options=list(stock_options.keys()), 
    default=["Apple Inc."]
)
tickers = [stock_options[name] for name in selected_stock_names]

# Period & chart type
st.sidebar.subheader("Chart Settings")
period = st.sidebar.selectbox("Time period:", ["1mo", "3mo", "6mo", "1y", "5y"])
show_candle = st.sidebar.checkbox("Show Candlestick Chart", value=False)

# Moving averages
ma20_window = st.sidebar.slider("MA20 Window", 5, 50, 20)
ma50_window = st.sidebar.slider("MA50 Window", 20, 200, 50)

# Metrics toggle
st.sidebar.subheader("Metrics Options")
show_rsi = st.sidebar.checkbox("RSI (Relative Strength Index)", value=True)
show_sharpe = st.sidebar.checkbox("Sharpe Ratio", value=True)
show_drawdown = st.sidebar.checkbox("Max Drawdown", value=True)

# Portfolio settings 
st.sidebar.subheader("Portfolio Settings")
enable_portfolio = st.sidebar.checkbox("Enable Portfolio View", value=False)
if enable_portfolio:
    portfolio_stock_names = st.sidebar.multiselect(
        "Select portfolio stocks:", 
        options=list(stock_options.keys()), 
        default=["Apple Inc.", "Microsoft Corporation", "Tesla, Inc."]
    )
    portfolio_tickers = [stock_options[name] for name in portfolio_stock_names]
    default_weights = [1/len(portfolio_tickers)] * len(portfolio_tickers)
    weights_input = st.sidebar.text_input(
        "Weights (comma-separated, sum to 1):",
        ",".join([str(w) for w in default_weights])
    )
    weights = [float(w.strip()) for w in weights_input.split(",")]
    if abs(sum(weights) - 1) > 0.01:
        st.sidebar.error("Weights must sum to 1")

# Helper Function #
@st.cache_data
def get_data(ticker, period):
    df = yf.Ticker(ticker).history(period=period)
    df["MA20"] = df["Close"].rolling(ma20_window).mean()
    df["MA50"] = df["Close"].rolling(ma50_window).mean()
    df["Returns"] = df["Close"].pct_change()
    df["Cumulative"] = (1 + df["Returns"]).cumprod()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Drawdown
    rolling_max = df['Cumulative'].cummax()
    df['Drawdown'] = (df['Cumulative'] - rolling_max) / rolling_max
    
    # Sharpe Ratio
    mean_return = df['Returns'].mean()
    volatility = df['Returns'].std()
    df['Sharpe'] = mean_return / volatility * (252**0.5) if volatility != 0 else 0
    
    return df

# Single-stock Dashboard #
for ticker in tickers:
    st.subheader(f"{ticker} Performance")
    data = get_data(ticker, period)
    
    # Chart
    if not show_candle:
        fig = px.line(
            data, x=data.index, y=["Close", "MA20", "MA50"],
            title=f"{ticker} Price & Moving Averages",
            color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c"]
        )
    else:
        fig = go.Figure(data=[go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'],
            low=data['Low'], close=data['Close'], name="Candlestick"
        )])
        fig.add_scatter(x=data.index, y=data["MA20"], mode="lines", name=f"MA{ma20_window}", line=dict(color="#ff7f0e"))
        fig.add_scatter(x=data.index, y=data["MA50"], mode="lines", name=f"MA{ma50_window}", line=dict(color="#2ca02c"))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Moving Average Explanation
    st.markdown(
        "**Moving Averages (MA):**\n"
        "- **MA20 (20-day moving average):** Average closing price of the last 20 trading days. Short-term trend indicator.\n"
        "- **MA50 (50-day moving average):** Average closing price of the last 50 trading days. Medium-term trend indicator."
    )
    
    # Metrics # 
    st.markdown("### Metrics Insights")
    
    if show_rsi:
        fig_rsi = px.line(data, x=data.index, y="RSI", title=f"{ticker} RSI")
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
        st.plotly_chart(fig_rsi, use_container_width=True)
        st.markdown(
            "**RSI (Relative Strength Index):** Measures the speed and change of price movements. "
            "Values above 70 indicate overbought conditions; below 30 indicate oversold conditions. "
            "Calculated as 100 - (100 / (1 + RS)), where RS = average gain / average loss over 14 periods."
        )
    
    if show_sharpe:
        st.write(f"Sharpe Ratio: {data['Sharpe'].iloc[-1]:.2f}")
        st.markdown(
            "The **Sharpe Ratio** indicates risk-adjusted return. "
            "It is calculated as the average return divided by the standard deviation of returns, annualized: "
            "Sharpe = (mean return / standard deviation of return) * sqrt(252)."
        )
    
    if show_drawdown:
        st.write(f"Max Drawdown: {data['Drawdown'].min():.2%}")
        st.markdown(
            "**Max Drawdown:** Largest peak-to-trough decline in cumulative returns. "
            "Represents the maximum potential loss an investor could experience."
        )

# Portfolio Dashboard #
if enable_portfolio and len(weights) == len(portfolio_tickers):
    st.subheader("Portfolio Performance")
    st.markdown("Shows how your selected stocks perform together based on chosen weights.")
    
    portfolio_data = pd.DataFrame()
    for ticker, weight in zip(portfolio_tickers, weights):
        df = get_data(ticker, period)
        df['Weighted_Return'] = df['Returns'] * weight
        if portfolio_data.empty:
            portfolio_data['Cumulative'] = (1 + df['Weighted_Return']).cumprod()
            portfolio_data['Daily_Return'] = df['Weighted_Return']
        else:
            portfolio_data['Cumulative'] *= (1 + df['Weighted_Return'])
            portfolio_data['Daily_Return'] += df['Weighted_Return']
    
    mean_ret = portfolio_data['Daily_Return'].mean()
    vol = portfolio_data['Daily_Return'].std()
    sharpe = mean_ret / vol * (252**0.5) if vol != 0 else 0
    
    rolling_max = portfolio_data['Cumulative'].cummax()
    drawdown = (portfolio_data['Cumulative'] - rolling_max) / rolling_max
    
    fig_port = px.line(portfolio_data, y='Cumulative', title="Portfolio Cumulative Growth", color_discrete_sequence=["#9467bd"])
    st.plotly_chart(fig_port, use_container_width=True)
    
    st.write(f"Portfolio Sharpe Ratio: {sharpe:.2f}")
    st.markdown(
        "The **Portfolio Sharpe Ratio** measures risk-adjusted performance of the combined portfolio "
        "taking into account weights of each stock and their returns."
    )
    st.write(f"Portfolio Max Drawdown: {drawdown.min():.2%}")
    st.markdown(
        "The **Portfolio Max Drawdown** indicates the largest cumulative loss from peak to trough "
        "across the weighted portfolio."
    )

# Footer #
st.markdown("---")
st.markdown("Created by Preet Harquissandas")
