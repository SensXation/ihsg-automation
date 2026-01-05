import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, text
import toml
import os # Added import os

# Gunakan daftar ticker yang sama persis dengan etl_pipeline
from etl_pipeline import TICKERS 

# CONFIGURATION
try:
    secrets = toml.load(".streamlit/secrets.toml")
    DB_URL = secrets.get("db_url")
except FileNotFoundError:
    DB_URL = os.getenv("DATABASE_URL")

def backfill_data():
    if not DB_URL or "PASTE_YOUR" in str(DB_URL):
        print("❌ Error: Invalid Database URL.")
        return

    print("🔌 Connecting to Supabase...")
    engine = create_engine(DB_URL)
    
    # WARNING: Ini menghapus semua data lama dan isi ulang
    print("🧹 TRUNCATING table...")
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE daily_stock_prices"))
        conn.commit()
    
    print("📥 Downloading data from Start of 2024...")
    
    for ticker in TICKERS:
        try:
            # Download data from 2024-01-01
            data = yf.download(ticker, start="2024-01-01", progress=False)
            
            if not data.empty:
                df = data[['Open', 'High', 'Low', 'Close', 'Volume']].reset_index()
                df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
                df = df.round(2)
                df['ticker'] = ticker
                
                df.to_sql('daily_stock_prices', engine, if_exists='append', index=False)
                print(f"   ✅ {ticker}: Loaded {len(df)} rows")
            else:
                print(f"   ⚠️ {ticker}: No data")
                
        except Exception as e:
            print(f"   ❌ {ticker}: Failed ({e})")

    print("\n🎉 Backfill Complete!")

if __name__ == "__main__":
    backfill_data()