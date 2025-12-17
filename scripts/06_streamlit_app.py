# scripts/06_streamlit_app.py
import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS_DIR = os.path.join(BASE, "analysis_outputs")
CHARTS_DIR = os.path.join(BASE, "charts")

# Files
summary_file = os.path.join(ANALYSIS_DIR, "metrics_summary.csv")
metrics_by_symbol = os.path.join(ANALYSIS_DIR, "metrics_by_symbol.csv")
daily_file = os.path.join(ANALYSIS_DIR, "nifty50_analysis.csv")

st.set_page_config(page_title="Nifty50 Dashboard", layout="wide")
st.title("📊 Nifty50 Stock Dashboard")

# Load summary
if not os.path.exists(summary_file):
    st.error(f"Missing file: {summary_file}. Run analysis first.")
    st.stop()
summary = pd.read_csv(summary_file)

# Load per-symbol metrics
if os.path.exists(metrics_by_symbol):
    sym_metrics = pd.read_csv(metrics_by_symbol)
else:
    st.warning("metrics_by_symbol.csv not found. Attempting to compute on the fly...")
    if not os.path.exists(daily_file):
        st.error("nifty50_analysis.csv missing as well. Run analysis.")
        st.stop()
    df_temp = pd.read_csv(daily_file, parse_dates=["Date"])
    sym_metrics = df_temp.groupby("Symbol").agg(
        Avg_Daily_Return=("Daily_Return","mean"),
        Volatility=("Daily_Return","std"),
        Last_Close=("Close","last"),
        Avg_Volume=("Volume","mean"),
        Total_Cumulative_Return=("Cumulative_Return","last")
    ).reset_index()

# Load daily data
if os.path.exists(daily_file):
    daily = pd.read_csv(daily_file, parse_dates=["Date"])
else:
    st.error(f"Missing daily file: {daily_file}")
    st.stop()

# KPIs from summary
st.subheader("Market Summary")
cols = st.columns(4)
cols[0].metric("Total Stocks", int(summary["total_stocks"].iloc[0]))
cols[1].metric("Green Stocks", int(summary["green_stocks"].iloc[0]))
cols[2].metric("Red Stocks", int(summary["red_stocks"].iloc[0]))
cols[3].metric("Best Stock", str(summary["best_stock"].iloc[0]))
st.write(f"Best stock cumulative return: {summary['best_stock_cum_return'].iloc[0]:.4f}")

# Top / Bottom lists
st.subheader("Top / Bottom Performers (by Total Cumulative Return)")
top = sym_metrics.sort_values("Total_Cumulative_Return", ascending=False).head(10)
bot = sym_metrics.sort_values("Total_Cumulative_Return", ascending=True).head(10)
c1, c2 = st.columns(2)
with c1:
    st.write("Top 10")
    st.dataframe(top.reset_index(drop=True))
with c2:
    st.write("Bottom 10")
    st.dataframe(bot.reset_index(drop=True))

# Symbol selection and single-stock charts
st.subheader("Stock Viewer")
symbols = sorted(daily["Symbol"].unique())
sel_sym = st.selectbox("Select symbol", symbols, index=0)

sym_df = daily[daily["Symbol"] == sel_sym].sort_values("Date")
if sym_df.empty:
    st.warning("No data for selected symbol")
else:
    # Price chart
    st.write(f"### {sel_sym} — Price")
    st.line_chart(sym_df.set_index("Date")["Close"])

    # Cumulative return
    if "Cumulative_Return" in sym_df.columns:
        st.write(f"### {sel_sym} — Cumulative Return")
        st.line_chart(sym_df.set_index("Date")["Cumulative_Return"])
    else:
        st.info("Cumulative_Return not available for this stock.")

# Compare two stocks
st.subheader("Compare two stocks (Cumulative Return)")
sym1, sym2 = st.selectbox("Stock A", symbols, index=0), st.selectbox("Stock B", symbols, index=1)
df1 = daily[daily["Symbol"] == sym1].set_index("Date").sort_index()
df2 = daily[daily["Symbol"] == sym2].set_index("Date").sort_index()

plt.figure(figsize=(10,5))
if "Cumulative_Return" in df1.columns:
    plt.plot(df1.index, df1["Cumulative_Return"], label=sym1)
if "Cumulative_Return" in df2.columns:
    plt.plot(df2.index, df2["Cumulative_Return"], label=sym2)
plt.legend()
plt.title("Cumulative Return Comparison")
plt.xlabel("Date")
plt.grid(True)
st.pyplot(plt)

st.write("Charts available in the `charts/` folder for quick preview.")
