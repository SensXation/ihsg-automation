import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta


import data_processor 


st.set_page_config(
    page_title="IHSG Pro Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Dark Theme Backgrounds */
    .stApp { background-color: #0e1117; }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] { background-color: #161b22; }
    
    /* Metrics Styling */
    div[data-testid="stMetricValue"] { font-size: 28px !important; }
    
    /* Hide Plotly Modebar partially */
    .modebar-container { opacity: 0.3 !important; }
    .modebar-container:hover { opacity: 1 !important; }
</style>
""", unsafe_allow_html=True)


def render_tradingview_chart(df, ma50, ma200):
    """Function specifically to render TradingView-style charts"""
   
    # Calculate Moving Averages (Visual Only)
    if ma50: df['MA50'] = df['close'].rolling(window=50).mean()
    if ma200: df['MA200'] = df['close'].rolling(window=200).mean()

    # Create Subplots
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.02, 
        row_heights=[0.75, 0.25]
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df['date'],
        open=df['open'], high=df['high'], low=df['low'], close=df['close'],
        name='Price',
        increasing_line_color='#26a69a', 
        decreasing_line_color='#ef5350', 
        showlegend=False
    ), row=1, col=1)

    # Moving Averages
    if ma50:
        fig.add_trace(go.Scatter(x=df['date'], y=df['MA50'], line=dict(color='#FF9800', width=1.5), name='MA 50'), row=1, col=1)
    if ma200:
        fig.add_trace(go.Scatter(x=df['date'], y=df['MA200'], line=dict(color='#2196F3', width=1.5), name='MA 200'), row=1, col=1)

    # Volume Bar
    colors = ['#26a69a' if c >= o else '#ef5350' for c, o in zip(df['close'], df['open'])]
    fig.add_trace(go.Bar(
        x=df['date'], y=df['volume'], marker_color=colors, name='Volume', opacity=0.5, showlegend=False
    ), row=2, col=1)

    # Layout Styling
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=600,
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
        xaxis_rangeslider_visible=False,
        modebar=dict(
            orientation='h',      
            yanchor='bottom',     
            y=1,                  
            xanchor='right',      
            x=1,                  
            bgcolor='rgba(0,0,0,0)', 
            color='#ffffff'       
        )
    )
    
    # Grid Styling
    fig.update_yaxes(gridcolor='#333333', row=1, col=1)
    fig.update_yaxes(visible=False, row=2, col=1)
    
    return fig


def main():
  
    st.sidebar.title("🔍 Market Scanner")
    
    # Call Data Processor: Get Ticker List
    ticker_map = data_processor.get_ticker_list()
    
    if not ticker_map:
        st.warning("Database Empty/Error.")
        return

    
    display_names = list(ticker_map.keys())
    selected_display = st.sidebar.selectbox("Select Stock", display_names)
    selected_real_ticker = ticker_map[selected_display]

    st.sidebar.subheader("Chart Settings")
    time_range = st.sidebar.select_slider("Time Range", options=["1M", "3M", "6M", "1Y", "All"], value="6M")
    col_ma1, col_ma2 = st.sidebar.columns(2)
    show_ma50 = col_ma1.checkbox("MA 50", value=True)
    show_ma200 = col_ma2.checkbox("MA 200", value=False)

    try:
        # Call Data Processor: Get Stock Data
        df = data_processor.get_stock_data(selected_real_ticker)
        
        # Date Filter Logic
        if time_range != "All":
            days_map = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365}
            start_date = df['date'].max() - timedelta(days=days_map[time_range])
            df = df[df['date'] >= start_date]

        # Call Data Processor: Calculate KPI
        price, diff, pct, is_positive = data_processor.calculate_kpi(df)
        
        # --- DISPLAY KPI ---
        last_date = df['date'].iloc[-1].strftime('%d %b %Y')
        color_text = "#26a69a" if is_positive else "#ef5350"
        
        col1, col2, col3 = st.columns([1, 2, 4])
        with col1:
            st.markdown(f"<h1 style='margin:0; padding:0;'>{selected_display}</h1>", unsafe_allow_html=True)
            st.caption(f"Last Updated: {last_date}")
        with col2:
            st.metric("Last Price", f"Rp {price:,.0f}")
        with col3:
            st.markdown(f"""
            <div style="font-size: 14px; color: gray; margin-bottom: 0px;">Daily Change</div>
            <div style="font-size: 26px; font-weight: bold; color: {color_text};">
                {diff:,.0f} ({pct:.2f}%)
            </div>
            """, unsafe_allow_html=True)
            
        st.divider()

        # --- DISPLAY CHART ---
        chart_fig = render_tradingview_chart(df, show_ma50, show_ma200)
        st.plotly_chart(chart_fig, use_container_width=True)

        # --- DISPLAY TABLE ---
        with st.expander(f"📊 View Historical Data for {selected_display}"):
            st.dataframe(df.sort_values('date', ascending=False), use_container_width=True)

    except Exception as e:
        st.error(f"Application error occurred: {e}")

if __name__ == "__main__":
    main()