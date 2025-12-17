# scripts/02_clean_data.py
import os
import glob
import pandas as pd

RAW_DIR = "data"
CLEAN_DIR = "cleaned"
os.makedirs(CLEAN_DIR, exist_ok=True)

print("Cleaning individual CSVs and creating combined cleaned CSV...")

# find per-symbol CSVs (skip combined if exists)
files = glob.glob(os.path.join(RAW_DIR, "*.csv"))
per_symbol = [f for f in files if not f.endswith("nifty50_all.csv")]

cleaned_list = []

for f in per_symbol:
    try:
        df = pd.read_csv(f)
        # Ensure columns exist
        required = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume", "Symbol"]
        # Some CSVs from yfinance use 'Adj Close' while earlier sample used 'Close' only. Normalize:
        # If 'Adj Close' exists, we'll keep 'Close' as is and compute returns on 'Close' (raw)
        # Ensure Date parsing
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        else:
            # Try first column as date
            df.columns = ["Date"] + list(df.columns[1:])
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        # Symbol column (some CSVs may lack Symbol)
        filename_symbol = os.path.splitext(os.path.basename(f))[0].replace("_", ".")
        if "Symbol" not in df.columns:
            df["Symbol"] = filename_symbol

        # Drop rows with invalid dates
        df = df.dropna(subset=["Date"])
        df = df.sort_values("Date").reset_index(drop=True)

        # Ensure numeric types
        for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Drop rows without Close
        df = df.dropna(subset=["Close"])

        # Save cleaned per-symbol
        out_path = os.path.join(CLEAN_DIR, f"{filename_symbol}.csv")
        df.to_csv(out_path, index=False)
        cleaned_list.append(df)
    except Exception as e:
        print("Failed to clean", f, e)

if cleaned_list:
    combined = pd.concat(cleaned_list, ignore_index=True)
    combined.to_csv(os.path.join(CLEAN_DIR, "nifty50_cleaned.csv"), index=False)
    print("Saved combined cleaned CSV:", os.path.join(CLEAN_DIR, "nifty50_cleaned.csv"))

print("Cleaning completed.")
