# imports
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# -------------------
# Page title & description
# -------------------
st.title('📈 Stock Visualisation and Predictor')
st.markdown("""
A simple ML-based stock predictor built with Streamlit and yfinance.
Enter a ticker, select a date range, and visualise the stock prices.
""")

# -------------------
# User Inputs
# -------------------
ticker = st.text_input(
    "Enter the Stock Symbol (e.g., AAPL, TSLA, MSFT, NVDA, PLTR):",
    "TSLA"
)

start_date = st.date_input("Start date", datetime(2020, 1, 1))
end_date = st.date_input("End date", datetime.today())

# -------------------
# Load Data Function
# -------------------


@st.cache_data
def load_data(ticker, start, end):
    # convert dates to datetime
    start = datetime.combine(start, datetime.min.time())
    end = datetime.combine(end + timedelta(days=1), datetime.min.time())

    # download data
    data = yf.download(ticker, start, end)

    if data.empty:
        return pd.DataFrame()  # return empty DF if no data

    # reset index
    data.reset_index(inplace=True)

    # flatten MultiIndex columns (sometimes returned by yfinance)
    data.columns = [col[0] if isinstance(
        col, tuple) else col for col in data.columns]

    return data


# -------------------
# Show Stock Prices Button
# -------------------
if st.button("Show Stock Prices"):
    stock_data = load_data(ticker, start_date, end_date)

    if stock_data.empty:
        st.warning("No data found for this ticker/date range.")
    else:
        st.subheader(f"Requested Stock Data")
        st.write(stock_data.tail())

# -------------------
# Session state for chart button
# -------------------
if "show_chart" not in st.session_state:
    st.session_state.show_chart = False

if st.button("Visualise Changes in Prices"):
    st.session_state.show_chart = True

# -------------------
# Plot Candlestick Chart
# -------------------
if st.session_state.show_chart:
    stock_data = load_data(ticker, start_date, end_date)

    if stock_data.empty:
        st.warning("No data to display in chart.")
    else:
        # find the date column automatically
        date_col = [col for col in stock_data.columns
                    if str(col).lower() in ("date", "datetime")][0]

        # create candlestick figure
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=stock_data[date_col],
                    open=stock_data['Open'],
                    high=stock_data['High'],
                    low=stock_data['Low'],
                    close=stock_data['Close'],
                    name=ticker
                )
            ]
        )

        fig.update_layout(
            title=f"{ticker} Stock Price",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(fig, use_container_width=True)
