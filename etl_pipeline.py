import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
import toml  
import os
from datetime import datetime

# --- CONFIGURATION ---

try:
    secrets = toml.load(".streamlit/secrets.toml")
    DB_URL = secrets.get("db_url") 
except FileNotFoundError:
    print("❌ Could not find .streamlit/secrets.toml")
    DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    raise ValueError("❌ DB_URL not found! Check your .streamlit/secrets.toml file.")

# 2. Target Stocks (Updated List)
TICKERS = [
    'ARCI.JK', 'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BUMI.JK', 
    'BULL.JK', 'BKSL.JK', 'GOTO.JK', 'MINA.JK', 'PANI.JK'
]

def extract_data(ticker_list):
    print(f"🚀 Starting extraction...")
    all_data = []
    
    for ticker in ticker_list:
        try:
            stock = yf.Ticker(ticker)
            # Fetch 1 month to ensure we get data
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
        final_df = pd.concat(all_data)
        
        # --- NEW: ROUND NUMBERS TO 2 DECIMALS ---
        # Rounds open, high, low, close. Leaves volume as is.
        cols_to_round = ['open', 'high', 'low', 'close']
        final_df[cols_to_round] = final_df[cols_to_round].round(2)
        # ----------------------------------------
        
        return final_df
        
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
        if "unique constraint" in str(e).lower():
            print("⚠️ Data for today already exists. Skipping load.")
        else:
            print(f"❌ Database Error: {e}")

if __name__ == "__main__":
    daily_df = extract_data(TICKERS)
    if not daily_df.empty:
        load_data(daily_df, DB_URL)