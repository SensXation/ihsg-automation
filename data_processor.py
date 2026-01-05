import streamlit as st
import pandas as pd
from sqlalchemy import create_engine


@st.cache_resource
def get_engine():
    return create_engine(st.secrets["db_url"])

@st.cache_data(ttl=3600)
def get_ticker_list():
    engine = get_engine()
    query = "SELECT DISTINCT ticker FROM daily_stock_prices ORDER BY ticker"
    
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    
    raw_tickers = df['ticker'].tolist()
    
    ticker_map = {t.replace('.JK', ''): t for t in raw_tickers}
    return ticker_map

@st.cache_data(ttl=300) 
def get_stock_data(real_ticker_code):
    engine = get_engine()
    query = f"""
    SELECT date, open, high, low, close, volume 
    FROM daily_stock_prices 
    WHERE ticker = '{real_ticker_code}'
    ORDER BY date ASC
    """
    
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    
    df['date'] = pd.to_datetime(df['date'])
    return df

def calculate_kpi(df):
    if df.empty:
        return 0, 0, 0, False

    last_row = df.iloc[-1]
    prev_row = df.iloc[-2] if len(df) > 1 else last_row
    
    latest_price = last_row['close']
    diff = latest_price - prev_row['close']
    pct = (diff / prev_row['close']) * 100 if prev_row['close'] != 0 else 0
    is_positive = diff >= 0
    
    return latest_price, diff, pct, is_positive