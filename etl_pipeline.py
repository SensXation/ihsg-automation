import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
import toml
import os
from datetime import datetime


TICKERS = [
    'ARCI.JK', 'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BUMI.JK', 
    'BULL.JK', 'BKSL.JK', 'GOTO.JK', 'MINA.JK', 'PANI.JK',
    'ANTM.JK', 'BBYB.JK', 'BRMS.JK', 'BUVA.JK', 'ENRG.JK', 'GTSI.JK', 'MEJA.JK'
]

def get_db_url():
    """Securely retrieve Database URL."""
    try:
        secrets = toml.load(".streamlit/secrets.toml")
        return secrets.get("db_url")
    except FileNotFoundError:
        return os.getenv("DATABASE_URL")

def extract_data(ticker_list):
    """Fetch latest stock data from Yahoo Finance."""
    print(f"🚀 Starting extraction for {len(ticker_list)} stocks...")
    all_data = []
    
    for ticker in ticker_list:
        try:
           
            stock = yf.Ticker(ticker)
            df = stock.history(period="5d")
            
            if not df.empty:
                df.reset_index(inplace=True)
                df['ticker'] = ticker
                df['date'] = df['Date'].dt.date
                
                # Standardize columns
                df = df.rename(columns={
                    "Open": "open", "High": "high", "Low": "low", 
                    "Close": "close", "Volume": "volume"
                })
                
                # Keep only latest row (Today)
                latest_df = df.tail(1)[['date', 'ticker', 'open', 'high', 'low', 'close', 'volume']]
                all_data.append(latest_df)
                print(f"   ✅ Fetched {ticker}")
            else:
                print(f"   ⚠️ No data for {ticker}")
                
        except Exception as e:
            print(f"   ❌ Error {ticker}: {e}")

    if all_data:
        final_df = pd.concat(all_data)
        cols_to_round = ['open', 'high', 'low', 'close']
        final_df[cols_to_round] = final_df[cols_to_round].round(2)
        return final_df
        
    return pd.DataFrame()

def load_data(df, db_url):
    """Load data to Supabase with duplicate prevention."""
    if df.empty or not db_url: return

    print(f"📦 Loading {len(df)} rows to Database...")
    engine = create_engine(db_url)

    try:
        with engine.connect() as conn:
            df.to_sql('daily_stock_prices', con=conn, if_exists='append', index=False)
            print("🎉 SUCCESS: Data loaded!")
    except Exception as e:
        if "unique constraint" in str(e).lower():
            print("ℹ️ Data for today already exists. Skipped.")
        else:
            print(f"❌ Database Error: {e}")

if __name__ == "__main__":
    url = get_db_url()
    if url:
        daily_df = extract_data(TICKERS)
        load_data(daily_df, url)
    else:
        print("❌ DB Connection failed.")