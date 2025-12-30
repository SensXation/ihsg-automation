import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, text

# --- CONFIGURATION ---
DB_URL = "postgresql://postgres.qkedvgwpmblqdjbvwatf:Willsenricky123!@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"

# [UPDATED] New Ticker List for Backfill
TICKERS = [
    'ARCI.JK', 'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BUMI.JK', 
    'BULL.JK', 'BKSL.JK', 'GOTO.JK', 'MINA.JK', 'PANI.JK'
]

def backfill_data():
    if "PASTE_YOUR" in DB_URL:
        print("❌ ERROR: Paste your Database URL in the script first!")
        return

    print("🔌 Connecting to Supabase...")
    engine = create_engine(DB_URL)
    
    # 1. CLEAN SLATE (Optional: Comment this out if you want to KEEP old data)
    # Since you changed tickers completely, wiping it is cleaner so you don't have "dead" stocks like TLKM/BBNI mixing in.
    print("🧹 Clearing data to start fresh...")
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE daily_stock_prices"))
        conn.commit()
    
    print("📥 Downloading 2025 data (Full OHLC)...")
    
    for ticker in TICKERS:
        print(f"   Downloading {ticker}...")
        try:
            # Download everything from Start of 2025
            data = yf.download(ticker, start="2025-01-01", progress=False)
            
            if not data.empty:
                # 2. SELECT ALL COLUMNS
                df_upload = data[['Open', 'High', 'Low', 'Close', 'Volume']].reset_index()
                
                # 3. RENAME columns to match Supabase (lowercase)
                df_upload.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
                df_upload[df_upload.columns] = df_upload[df_upload.columns].round(2)
                
                # 4. ADD Ticker Name
                df_upload['ticker'] = ticker
                
                # 5. UPLOAD
                df_upload.to_sql('daily_stock_prices', engine, if_exists='append', index=False)
                print(f"   ✅ Loaded {len(df_upload)} rows for {ticker}")
            else:
                print(f"   ⚠️ No data found for {ticker}")
                
        except Exception as e:
            print(f"   ❌ Failed to backfill {ticker}: {e}")

    print("\n🎉 BACKFILL COMPLETE! Your database now has history for the new stocks.")

if __name__ == "__main__":
    backfill_data()