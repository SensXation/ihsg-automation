import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
import os
from datetime import datetime

# --- CONFIGURATION ---
# 1. DATABASE CONNECTION 
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    raise ValueError("❌ DATABASE_URL is missing! Set it in your environment variables.")

#2. Target Stocks
TICKERS = ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK', 'TLKM.JK', 'GOTO.JK']

def extract_data(ticker_list):
    print(f"🚀 Starting extraction...")
    all_data = []
    
    for ticker in ticker_list:
        try:
           
            stock = yf.Ticker(ticker)
            
            # Fetch 1 month to ensure we get data even if market is closed today
            df = stock.history(period="1mo")
            
            if not df.empty:
                df.reset_index(inplace=True)
                df['ticker'] = ticker
                df['date'] = df['Date'].dt.date
                
                # Standardize columns
                df = df.rename(columns={
                    "Open": "open", "High": "high", "Low": "low", 
                    "Close": "close", "Volume": "volume"
                })
                
                # Keep only what we need
                df = df[['date', 'ticker', 'open', 'high', 'low', 'close', 'volume']]
                
                # Take only the LATEST row (Today's data)
                latest_df = df.tail(1)
                
                all_data.append(latest_df)
                print(f"   ✅ Fetched {ticker}: {latest_df['date'].values[0]}")
            else:
                print(f"   ⚠️ No data found for {ticker}")
                
        except Exception as e:
            print(f"   ❌ Error {ticker}: {e}")

    if all_data:
        return pd.concat(all_data)
    return pd.DataFrame()

def load_data(df, db_url):
    if df.empty:
        print("⚠️ No data to load.")
        return

    print(f"📦 Connecting to Cloud Database...")
    engine = create_engine(db_url)

    try:
        with engine.connect() as conn:
            df.to_sql('daily_stock_prices', con=conn, if_exists='append', index=False)
            print(f"🎉 SUCCESS: Loaded {len(df)} rows to Supabase!")
    except Exception as e:
        # Check for the unique constraint we created in SQL
        if "unique constraint" in str(e).lower():
            print("⚠️ Data for today already exists. Skipping load.")
        else:
            print(f"❌ Database Error: {e}")

if __name__ == "__main__":
    daily_df = extract_data(TICKERS)
    if not daily_df.empty:
        load_data(daily_df, DB_URL)