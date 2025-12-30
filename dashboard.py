import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# 1. SETUP PAGE
st.set_page_config(page_title="IHSG Automated Dashboard", layout="wide")
st.title("🇮🇩 IHSG Stock Tracker (Automated)")
st.markdown("This dashboard updates automatically every day via **GitHub Actions**.")

# 2. CONNECT TO DATABASE

try:
    db_url = st.secrets["db_url"]
    engine = create_engine(db_url)
    
    # 3. LOAD DATA
    
    query = """
    SELECT date, ticker, close 
    FROM daily_stock_prices 
    ORDER BY date DESC
    """
    
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    # 4. DASHBOARD VISUALS
    if not df.empty:
        # KPI Cards
        col1, col2, col3 = st.columns(3)
        latest_date = df['date'].max()
        unique_stocks = df['ticker'].nunique()
        total_rows = len(df)
        
        col1.metric("Last Update", str(latest_date))
        col2.metric("Stocks Tracked", unique_stocks)
        col3.metric("Total Data Points", total_rows)

        # Interactive Chart
        st.subheader("📈 Price Trends")
        tickers = df['ticker'].unique()
        selected = st.multiselect("Select Stocks", tickers, default=tickers[:2])
        
        if selected:
            filtered_df = df[df['ticker'].isin(selected)]
            fig = px.line(filtered_df, x='date', y='close', color='ticker', markers=True)
            st.plotly_chart(fig, use_container_width=True)
        
        # Data Table
        with st.expander("View Raw Data"):
            st.dataframe(df)
            
    else:
        st.warning("No data found in database yet!")

except Exception as e:
    st.error(f"Error connecting to database: {e}")