# scripts/01_download_all_stocks.py

import sys
import os
import time
import pandas as pd
import yfinance as yf

# ⭐ FIX: Add project root to Python import path ⭐
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Import tickers AFTER fixing sys.path
from utils.stock_list import NIFTY50_TICKERS

# Create data folder
DATA_DIR = os.path.join(ROOT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

print("Downloading data for Nifty50 tickers...")

combined = []
errors = []

for symbol in NIFTY50_TICKERS:
    print(f"Downloading {symbol} ...", end=" ")
    try:
        df = yf.download(symbol, period="1y", progress=False, auto_adjust=False)

        if df.empty:
            print("-> no data")
            errors.append(symbol)
            continue

        # Standardize columns and add Symbol column
        df = df.reset_index()
        df["Symbol"] = symbol

        # Save each stock CSV
        out_path = os.path.join(DATA_DIR, f"{symbol.replace('.', '_')}.csv")
        df.to_csv(out_path, index=False)

        combined.append(df)
        print("✔")

        # Avoid rate-limit issues
        time.sleep(0.5)

    except Exception as e:
        print("✖", e)
        errors.append(symbol)

# Save combined CSV
if combined:
    all_df = pd.concat(combined, ignore_index=True)
    full_path = os.path.join(DATA_DIR, "nifty50_all.csv")
    all_df.to_csv(full_path, index=False)
    print(f"\nSaved combined CSV: {full_path}")

# Error reporting
if errors:
    print("\nThe following tickers failed to download:")
    print(", ".join(errors))

print("\nDownload step completed.")
