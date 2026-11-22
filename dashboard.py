import pandas as pd
import streamlit as st
from src.analyzer import fetch_stock_data, clean_stock_data, calculate_indicators, generate_statistics

st.set_page_config(page_title="Stock Market Data Analyzer", page_icon="📈", layout="wide")
st.title("📈 Stock Market Data Analyzer")
st.caption("Educational historical market analysis — not financial advice.")

ticker = st.text_input("Stock ticker", "RELIANCE.NS")
start = st.date_input("Start date", pd.Timestamp("2025-01-01"))
end = st.date_input("End date", pd.Timestamp.today())

if st.button("Analyze"):
    if start >= end:
        st.error("End date must be after start date.")
    else:
        with st.spinner("Fetching historical data..."):
            raw = fetch_stock_data(ticker, str(start), str(end))
        if raw is None:
            st.error("Data could not be fetched. Check the ticker and connection.")
        else:
            try:
                data = calculate_indicators(clean_stock_data(raw))
                stats = generate_statistics(data)
                c1, c2, c3 = st.columns(3)
                c1.metric("Latest adjusted close", f"{stats['last_close']:.2f}")
                c2.metric("Historical return", f"{stats['total_return']:.2f}%")
                c3.metric("Annualized volatility", f"{stats['annualized_volatility']:.2f}%")
                st.subheader("Historical adjusted closing price")
                st.line_chart(data.set_index("date")["close"])
                st.subheader("Moving averages")
                st.line_chart(data.set_index("date")[["close", "SMA_20", "SMA_50"]])
                st.subheader("Daily returns")
                st.bar_chart(data.set_index("date")["daily_return"])
                st.subheader("Risk summary")
                st.write(f"Maximum drawdown: {stats['maximum_drawdown']:.2f}%")
                st.write(f"Historical trend: {stats['trend']}")
                st.subheader("Recent observations")
                st.dataframe(data.tail(20), use_container_width=True)
            except Exception as exc:
                st.error(str(exc))
