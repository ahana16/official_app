# please run python3 -m streamlit run main.py
# ctrl-c to exit 

import streamlit as st
import yfinance as yf 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("Stock Trading Dashboard for Observational Decision Making 📈")
("An interactive web application to visualoze and analyze stock market data and trends for decision making")

st.sidebar.header('User Input Features')
# Sidebar for user input
st.sidebar.header("Input Options")
selected_stock = st.sidebar.text_input("Enter a stock ticker (e.g., AAPL, TSLA):", value="AAPL")
timeframe = st.sidebar.selectbox("Select timeframe:", options=["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y", "max"], index=3)
# Fetch stock data
def get_stock_data(ticker, period):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        return data
    except Exception as e:
        st.error(f"Failed to retrieve data for {ticker}: {e}")
        return None

data = get_stock_data(selected_stock, timeframe)

if data is not None:
    # Display current stock price
    st.subheader(f"Current Stock Price: {selected_stock}")
    try:
        latest_price = data['Close'][-1]
        st.metric(label="Price", value=f"${latest_price:.2f}")
    except Exception as e:
        st.error("Error calculating current price.")

 # Line chart for historical trends
    st.subheader("Historical Stock Trends")
    st.line_chart(data['Close'], use_container_width=True)

    # Bar chart for trading volume
    st.subheader("Trading Volume")
    st.bar_chart(data['Volume'], use_container_width=True)

    # Moving averages
    st.subheader("Moving Averages")
    ma_periods = [20, 50, 200]
    for ma in ma_periods:
        data[f"MA_{ma}"] = data['Close'].rolling(window=ma).mean()

    st.line_chart(data[["Close"] + [f"MA_{ma}" for ma in ma_periods]])

    # Volatility (standard deviation of returns)
    st.subheader("Volatility")
    data['Daily Returns'] = data['Close'].pct_change()
    volatility = data['Daily Returns'].rolling(window=20).std()
    st.line_chart(volatility, use_container_width=True)

    # RSI calculation
    st.subheader("Relative Strength Index (RSI)")
    def calculate_rsi(data, period=14):
        delta = data['Close'].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)

        avg_gain = pd.Series(gain).rolling(window=period).mean()
        avg_loss = pd.Series(loss).rolling(window=period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi


    # Comparison of multiple stocks
    st.sidebar.subheader("Compare Stocks")
    compare_stocks = st.sidebar.text_area("Enter stock tickers to compare (comma-separated):", value="MSFT,GOOG")
    compare_list = [ticker.strip() for ticker in compare_stocks.split(',')]

    if compare_list:
        comparison_data = {}
        for ticker in compare_list:
            compare_data = get_stock_data(ticker, timeframe)
            if compare_data is not None:
                comparison_data[ticker] = compare_data['Close']

        if comparison_data:
            st.subheader("Stock Comparison")
            comparison_df = pd.DataFrame(comparison_data)
            st.line_chart(comparison_df)

    # Candlestick chart
    st.subheader("Candlestick Chart")
    try:
        import plotly.graph_objects as go

        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close']
        )])
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        st.error("Plotly is not installed. Install it to enable the candlestick chart feature.")

    # Save data to CSV
    st.subheader("Download Stock Data")
    csv = data.to_csv().encode('utf-8')
    st.download_button(
        label="Download Data as CSV",
        data=csv,
        file_name=f"{selected_stock}_data.csv",
        mime="text/csv"
    )

    # Customization options
    st.sidebar.header("Customization Options")
    selected_indicators = st.sidebar.multiselect(
        "Select indicators to display:",
        options=["Moving Averages", "Volatility", "RSI"],
        default=["Moving Averages", "Volatility", "RSI"]
    )

    if "Moving Averages" in selected_indicators:
        st.subheader("Moving Averages")
        st.line_chart(data[["Close"] + [f"MA_{ma}" for ma in ma_periods]])

    if "Volatility" in selected_indicators:
        st.subheader("Volatility")
        st.line_chart(volatility, use_container_width=True)

    st.write("Use the sidebar to customize your view and explore more features")
