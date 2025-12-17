# scripts/05_visualize.py
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-GUI backend for saving images
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

BASE = os.path.dirname(os.path.dirname(__file__))
ANALYSIS_DIR = os.path.join(BASE, "analysis_outputs")
CHARTS_DIR = os.path.join(BASE, "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)

INPUT = os.path.join(ANALYSIS_DIR, "nifty50_analysis.csv")
if not os.path.exists(INPUT):
    raise FileNotFoundError(f"Expected analysis file not found: {INPUT}")

print("Creating visualizations...")

# load data
df = pd.read_csv(INPUT, parse_dates=["Date"])

# Prepare per-symbol metrics
grp = df.sort_values(["Symbol", "Date"]).groupby("Symbol")
metrics = grp.agg(
    Avg_Daily_Return=("Daily_Return", "mean"),
    Volatility=("Daily_Return", "std"),
    Last_Close=("Close", "last"),
    Avg_Volume=("Volume", "mean"),
    Total_Cumulative_Return=("Cumulative_Return", "last")
).reset_index()

# Save metrics_by_symbol for downstream use
metrics_by_symbol_path = os.path.join(ANALYSIS_DIR, "metrics_by_symbol.csv")
metrics.to_csv(metrics_by_symbol_path, index=False)
print("Saved metrics_by_symbol.csv:", metrics_by_symbol_path)

# Market-level summary chart: average close (index level)
avg_close = df.groupby("Date")["Close"].mean().reset_index()

plt.figure(figsize=(12,6))
plt.plot(avg_close["Date"], avg_close["Close"])
plt.title("NIFTY50 - Average Close Price (Across Symbols)")
plt.xlabel("Date")
plt.ylabel("Average Close Price")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "nifty50_avg_close.png"))
plt.close()

# Top 10 performers by Total_Cumulative_Return
top10 = metrics.sort_values("Total_Cumulative_Return", ascending=False).head(10)
plt.figure(figsize=(12,6))
sns.barplot(data=top10, x="Symbol", y="Total_Cumulative_Return")
plt.title("Top 10 Stocks by Total Cumulative Return")
plt.xlabel("Symbol")
plt.ylabel("Total Cumulative Return")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "top10_cumulative_return.png"))
plt.close()

# Bottom 10 performers
bot10 = metrics.sort_values("Total_Cumulative_Return", ascending=True).head(10)
plt.figure(figsize=(12,6))
sns.barplot(data=bot10, x="Symbol", y="Total_Cumulative_Return")
plt.title("Bottom 10 Stocks by Total Cumulative Return")
plt.xlabel("Symbol")
plt.ylabel("Total Cumulative Return")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "bottom10_cumulative_return.png"))
plt.close()

# Volatility top 10
top_vol = metrics.sort_values("Volatility", ascending=False).head(10)
plt.figure(figsize=(12,6))
sns.barplot(data=top_vol, x="Symbol", y="Volatility")
plt.title("Top 10 Most Volatile Stocks (Std Dev of Daily Return)")
plt.xlabel("Symbol")
plt.ylabel("Volatility (std dev)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "top10_volatility.png"))
plt.close()

# Daily return distribution (all daily returns)
plt.figure(figsize=(10,6))
plt.hist(df["Daily_Return"].dropna(), bins=80)
plt.title("Distribution of Daily Returns (All Stocks)")
plt.xlabel("Daily Return")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "daily_return_distribution.png"))
plt.close()

# Correlation matrix of pct changes (use pivot)
pivot_close = df.pivot_table(index="Date", columns="Symbol", values="Close")
pct = pivot_close.pct_change().dropna(how="all")
corr = pct.corr()
# Limit to top 30 symbols by data availability / variance for readability
if corr.shape[0] > 30:
    ranking = corr.abs().sum().sort_values(ascending=False).head(30).index
    corr_small = corr.loc[ranking, ranking]
else:
    corr_small = corr

plt.figure(figsize=(11,9))
sns.heatmap(corr_small, cmap="coolwarm", vmin=-1, vmax=1)
plt.title("Correlation Heatmap (Daily % change)")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "correlation_heatmap.png"))
plt.close()

# Save a representative chart per symbol: last year close trend (optional, may produce many files)
sample_symbols = metrics["Symbol"].tolist()
for sym in sample_symbols:
    sub = df[df["Symbol"] == sym].sort_values("Date")
    if sub.shape[0] < 2:
        continue
    plt.figure(figsize=(8,3))
    plt.plot(sub["Date"], sub["Close"])
    plt.title(f"{sym} - Close Price")
    plt.xticks(rotation=45)
    plt.tight_layout()
    safe_name = sym.replace("/", "_").replace(" ", "_")
    plt.savefig(os.path.join(CHARTS_DIR, f"{safe_name}_close.png"))
    plt.close()

print("Charts saved in:", CHARTS_DIR)
print("Visualization completed.")
