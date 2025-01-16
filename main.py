# please run python3 -m streamlit 
# ctrl-c to exit 

# Import necessary libraries
import streamlit as st  # Streamlit for building the web app
import yfinance as yf   # Yahoo Finance for fetching stock data
import pandas as pd     # Pandas for data manipulation
import numpy as np      # NumPy for numerical calculations
import matplotlib.pyplot as plt  # Matplotlib for plotting charts

# Set the title for the Streamlit app
st.title("Enhanced Stock Trading Dashboard 📊")
st.write("Analyze and customize stock trends, indicators, and charts for informed decision-making.")

# Sidebar for user input - used to interact with the user and allow customization
st.sidebar.header('User Input Features')

# Input for stock ticker symbol: Let the user enter the stock symbol (e.g., AAPL, TSLA)
selected_stock = st.sidebar.text_input("Enter a stock ticker (e.g., AAPL, TSLA):", value="AAPL")

# Date range input for custom analysis: Allow the user to select a start and end date for the stock data
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("today"))

# Dropdown for selecting what to visualize: Allow users to toggle which features to view
st.sidebar.header("Visualization Options")
selected_features = st.sidebar.multiselect(
    "Select features to display:",
    options=["Historical Trends", "Trading Volume", "Moving Averages", "RSI", "Volatility"],
    default=["Historical Trends", "Trading Volume", "Moving Averages"]
)

# Fetch stock data using yfinance
def get_stock_data(ticker, start, end):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=start, end=end)
        return data
    except Exception as e:
        st.error(f"Failed to retrieve data for {ticker}: {e}")
        return None

# Fetch data for the selected stock based on user input
data = get_stock_data(selected_stock, start_date, end_date)

# If data is successfully retrieved, proceed with displaying the dashboard
if data is not None:
    # Display the current stock price (latest closing price)
    st.subheader(f"Current Stock Price: {selected_stock}")
    try:
        latest_price = data['Close'][-1]
        st.metric(label="Price", value=f"${latest_price:.2f}")
    except Exception as e:
        st.error("Error calculating current price.")

    # Display Historical Stock Trends (line chart of closing prices)
    if "Historical Trends" in selected_features:
        st.subheader("Historical Stock Trends")
        st.line_chart(data['Close'], use_container_width=True)
        st.caption("X-axis: Time | Y-axis: Price ($)")

    # Display Trading Volume (bar chart)
    if "Trading Volume" in selected_features:
        st.subheader("Trading Volume")
        st.bar_chart(data['Volume'], use_container_width=True)
        st.caption("X-axis: Time | Y-axis: Volume")

    # Display Simple Moving Averages (SMA) for 20, 50, and 200-day periods
    if "Moving Averages" in selected_features:
        st.subheader("Simple Moving Averages (SMA)")
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['SMA_200'] = data['Close'].rolling(window=200).mean()
        st.line_chart(data[['Close', 'SMA_20', 'SMA_50', 'SMA_200']], use_container_width=True)
        st.caption("X-axis: Time | Y-axis: Price ($)")

    # Display Relative Strength Index (RSI) to indicate overbought or oversold conditions
    if "RSI" in selected_features:
        st.subheader("Relative Strength Index (RSI)")
                # Function to calculate RSI
        def calculate_rsi(data, period=14):
            delta = data['Close'].diff()
            gain = np.where(delta > 0, delta, 0)
            loss = np.where(delta < 0, -delta, 0)

            avg_gain = pd.Series(gain).rolling(window=period).mean()
            avg_loss = pd.Series(loss).rolling(window=period).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return rsi

        data['RSI'] = calculate_rsi(data)
        st.line_chart(data['RSI'], use_container_width=True)
        st.caption("X-axis: Time | Y-axis: RSI")

    # Display Volatility (Standard Deviation of Daily Returns)
    if "Volatility" in selected_features:
        st.subheader("Volatility (Standard Deviation of Returns)")
        data['Daily Returns'] = data['Close'].pct_change()
        data['Volatility'] = data['Daily Returns'].rolling(window=20).std()
        st.line_chart(data['Volatility'], use_container_width=True)
        st.caption("X-axis: Time | Y-axis: Volatility")

    # Display Candlestick Chart (Plotly chart for more detailed price movement)
    st.subheader("Candlestick Chart")
    try:
        import plotly.graph_objects as go

        # Create a candlestick chart using Plotly
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

    # Provide a button for the user to download the stock data as CSV
    st.subheader("Download Stock Data")
    csv = data.to_csv().encode('utf-8')
    st.download_button(
        label="Download Data as CSV",
        data=csv,
        file_name=f"{selected_stock}_data.csv",
        mime="text/csv"
    )  # Button to download the data as a CSV file

    st.write("Customize your experience using the sidebar. Explore key stock indicators and trends.")
