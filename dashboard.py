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
    
    /* FIX: Agar modebar (tombol zoom) terlihat jelas dan tidak transparan */
    .modebar-container { opacity: 0.8 !important; }
    .modebar-container:hover { opacity: 1 !important; }
</style>
""", unsafe_allow_html=True)


def render_tradingview_chart(df,):
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03, 
        row_heights=[0.8, 0.2] 
    )

   
    fig.add_trace(go.Candlestick(
        x=df['date'],
        open=df['open'], high=df['high'], low=df['low'], close=df['close'],
        name='Price',
        increasing_line_color='#26a69a', 
        decreasing_line_color='#ef5350', 
        showlegend=False
    ), row=1, col=1)

   

   
    colors = ['#26a69a' if c >= o else '#ef5350' for c, o in zip(df['close'], df['open'])]
    fig.add_trace(go.Bar(
        x=df['date'], y=df['volume'], marker_color=colors, name='Volume', opacity=0.5, showlegend=False
    ), row=2, col=1)

    
    fig.update_layout(
        
        margin=dict(l=10, r=10, t=40, b=10),
        
        height=600,
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        
    
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="left", 
            x=0,         
            bgcolor="rgba(0,0,0,0)"
        ),
        
        xaxis_rangeslider_visible=False, 


        modebar=dict(
            orientation='h',      
            bgcolor='rgba(0,0,0,0)', 
            color='#ffffff'       
        )
    )
    
  
    fig.update_yaxes(gridcolor='#333333', row=1, col=1)
    fig.update_yaxes(visible=False, row=2, col=1)
    
    return fig


def main():
  
    st.sidebar.title("🔍 Market Scanner")
    

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

    try:
        df = data_processor.get_stock_data(selected_real_ticker)
        
        if time_range != "All":
            days_map = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365}
            start_date = df['date'].max() - timedelta(days=days_map[time_range])
            df = df[df['date'] >= start_date]

        price, diff, pct, is_positive = data_processor.calculate_kpi(df)
        
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

        
        st.plotly_chart(use_container_width=True, config={'displayModeBar': True, 'displaylogo': False})

        with st.expander(f"📊 View Historical Data for {selected_display}"):
            st.dataframe(df.sort_values('date', ascending=False), use_container_width=True)

    except Exception as e:
        st.error(f"Application error occurred: {e}")

if __name__ == "__main__":
    main()