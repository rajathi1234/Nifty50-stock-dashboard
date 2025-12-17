import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(__file__))
CLEANED = os.path.join(BASE, "cleaned")
OUTPUT = os.path.join(BASE, "analysis_outputs")

os.makedirs(OUTPUT, exist_ok=True)

print("Running Analysis...")

all_data = []

# Load each cleaned CSV and recompute missing metrics
for file in os.listdir(CLEANED):
    if file.endswith(".csv"):
        path = os.path.join(CLEANED, file)
        df = pd.read_csv(path)

        # Ensure correct types
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        symbol = df["Symbol"].iloc[0]

        # Compute Daily Return
        df["Daily_Return"] = df["Close"].pct_change()

        # Fill NA return
        df["Daily_Return_filled"] = df["Daily_Return"].fillna(0)

        # Compute cumulative return
        df["Cumulative_Return"] = (1 + df["Daily_Return_filled"]).cumprod() - 1

        all_data.append(df)

# Combine all symbols into one DataFrame
combined_df = pd.concat(all_data)

# Save final combined analysis file
final_path = os.path.join(OUTPUT, "nifty50_analysis.csv")
combined_df.to_csv(final_path, index=False)

print(f"Saved analysis: {final_path}")

# --------- Generate summary metrics ---------
metrics = {
    "total_stocks": combined_df["Symbol"].nunique(),
    "green_stocks": (combined_df.groupby("Symbol")["Cumulative_Return"].last() > 0).sum(),
    "red_stocks": (combined_df.groupby("Symbol")["Cumulative_Return"].last() <= 0).sum(),
}

# best stock
cum = combined_df.groupby("Symbol")["Cumulative_Return"].last()
best_symbol = cum.idxmax()
metrics["best_stock"] = best_symbol
metrics["best_stock_cum_return"] = cum[best_symbol]

# Save metrics file
metrics_df = pd.DataFrame([metrics])
metrics_path = os.path.join(OUTPUT, "metrics_summary.csv")
metrics_df.to_csv(metrics_path, index=False)

print(f"Saved metrics summary: {metrics_path}")
