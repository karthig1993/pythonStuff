import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

st.title("Stock Price Predictor")

# -------------------
# User Inputs
# -------------------
ticker = st.text_input("Enter Stock Symbol:", "TSLA")
start_date = st.date_input("Start date", datetime(2020, 1, 1))
future_days = st.slider("Days to Predict Into the Future:", 1, 60, 7)

present_date = datetime.today().strftime("%Y-%m-%d")

# Load data


@st.cache_data
def load_stock_data(ticker, start_date):
    data = yf.download(ticker, start_date, present_date)
    data.reset_index(inplace=True)
    return data


if st.button("Predict Prices"):
    data = load_stock_data(ticker, start_date)

   # -------------------------------
    # AUTO-ADJUST FEATURE ENGINEERING
    # -------------------------------
    data["Prev Close"] = data["Close"].shift(1)
    data["High - Low"] = data["High"] - data["Low"]
    data["Open - Close"] = data["Open"] - data["Close"]

    # Rolling features only if enough rows
    use_MA10 = len(data) >= 20
    use_MA50 = len(data) >= 60

    if use_MA10:
        data["MA10"] = data["Close"].rolling(10).mean()
    if use_MA50:
        data["MA50"] = data["Close"].rolling(50).mean()

    data.dropna(inplace=True)

    # Build dynamic feature list
    features = ["Prev Close", "High - Low", "Open - Close"]

    if use_MA10:
        features.append("MA10")
    if use_MA50:
        features.append("MA50")

    target = "Close"

    # Let user know what features were used
    st.info(f"🧠 Model features used: {features}")

    # -------------------------------
    # SAFETY CHECK — MINIMUM DATA
    # -------------------------------
    if len(data) < 10:
        st.error(
            "Not enough data to train the model, even after auto-adjust. Use an earlier start date.")
        st.stop()

    X = data[features]
    y = data[target]

    # -------------------------------
    # TRAIN / TEST SPLIT
    # -------------------------------
    test_size = 0.2

    # Guarantee the test set is valid
    if len(data) * test_size < 1:
        test_size = 1 / len(data)  # smallest possible

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=123
    )

    # -------------------------------
    # TRAIN MODEL
    # -------------------------------
    model = RandomForestRegressor(n_estimators=500, random_state=123)
    model.fit(X_train, y_train)

    # -------------------------------
    # EVALUATE
    # -------------------------------
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    st.write(f"📉 **Mean Squared Error:** {mse:.4f}")

    # -------------------------------
    # FUTURE PREDICTIONS
    # -------------------------------
    st.subheader(f"🔮 {future_days}-Day Forecast")

    future_predictions = []
    last_row = data.iloc[-1].copy()

    for i in range(future_days):
        # Build dynamic feature row
        feature_dict = {
            "Prev Close": last_row["Close"],
            "High - Low": last_row["High"] - last_row["Low"],
            "Open - Close": last_row["Open"] - last_row["Close"],
        }

        if use_MA10:
            feature_dict["MA10"] = data["Close"].rolling(10).mean().iloc[-1]
        if use_MA50:
            feature_dict["MA50"] = data["Close"].rolling(50).mean().iloc[-1]

        feature_row = pd.DataFrame([feature_dict])

        next_close = model.predict(feature_row)[0]
        future_predictions.append(next_close)

        # Update for next iteration
        last_row["Close"] = next_close

    future_dates = pd.date_range(
        start=data["Date"].iloc[-1] + timedelta(days=1), periods=future_days)

    # Chart forecast
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=data["Date"], y=data["Close"], mode="lines", name="Historical"))
    fig2.add_trace(go.Scatter(
        x=future_dates, y=future_predictions, mode="lines", name="Forecast"))
    st.plotly_chart(fig2)

    st.write(pd.DataFrame(
        {"Date": future_dates, "Predicted Close": future_predictions}))
