# scripts/03_load_to_sql.py
import sqlite3
import pandas as pd
import os

DB_PATH = "nifty50.db"
CLEANED_CSV = os.path.join("cleaned", "nifty50_cleaned.csv")

print("Loading cleaned data into SQLite database:", DB_PATH)

if not os.path.exists(CLEANED_CSV):
    raise FileNotFoundError(f"Cleaned CSV not found at {CLEANED_CSV}. Run scripts/02_clean_data.py first.")

df = pd.read_csv(CLEANED_CSV)
# Normalize column names
df.columns = [c.strip() for c in df.columns]

conn = sqlite3.connect(DB_PATH)
# Write main table
df.to_sql("daily_prices", conn, if_exists="replace", index=False)

# Create a simple symbols table (unique symbols and last known sector placeholder)
symbols = df[["Symbol"]].drop_duplicates().reset_index(drop=True)
symbols["Sector"] = "Unknown"  # you can update this by providing sectors.csv
symbols.to_sql("symbols", conn, if_exists="replace", index=False)

conn.close()
print("✔ SQLite DB created at", DB_PATH)
print("Tables: daily_prices, symbols")
