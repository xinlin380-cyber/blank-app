import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(
    page_title="台股智能診斷 Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css');
.stApp { background-color: #0f172a; }
.metric-card {
        background: #1e293b; border: 1px solid #475569; padding: 1.5rem;
        border-radius: 0.75rem; transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); height: 140px;
    }
.metric-card:hover {
        transform: translateY(-4px); border-color: #3b82f6;
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.4);
    }
.card-title {
        color: #f8fafc; font-size: 0.875rem; font-weight: 600;
        margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;
    }
.card-value {
        color: #ffffff; font-size: 2.25rem; font-weight: 800;
        line-height: 1; text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
.card-delta {
        color: #e2e8f0; font-size: 0.8rem; margin-top: 0.5rem; font-weight: 500;
    }
.positive { color: #22c55e!important; font-weight: 700; }
.negative { color: #ef4444!important; font-weight: 700; }
.neutral { color: #facc15!important; font-weight: 700; }
    h1, h2, h3, h4 { color: #ffffff!important; }
.stTextInput > div > div > input {
        background-color: #1e293b; color: #ffffff;
        border: 1px solid #475569; font-size: 1.1rem;
    }
.stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white; font-weight: 700; border: none; font-size: 1.1rem;
    }
.score-badge {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    font-weight: 800;
    font-size: 1.5rem;
    color: white;
}
.score-high { background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); }
.score-mid { background: linear-gradient(135deg, #facc15 0%, #d97706 100%); }
.score-low { background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); }
</style>
""", unsafe_allow_html=True)

st.markdown("                                     
st.markdown("# 📊 台股智能診斷系統 Pro")
st.markdown("<p style='color:                                                                                                                                 

col1, col2 = st.columns([3, 1])
with col1:
    code = st.text_input("輸入台股代號", value="2330", label_visibility="collapsed", placeholder="例如: 2360、0050、2330")
with col2:
    run = st.button("🚀 開始診斷", use_container_width=True, type="primary")

@st.cache_data(ttl=300)
def get_stock_data(ticker, period="6mo"):
    try:
        stock = yf.Ticker(f"{ticker}.TW")
        hist = stock.history(period=period)
        info = stock.info
        return hist, info
    except:
        return None, None

def calculate_rsi(data, period=14):
    delta = data['#cbd5e1; font-size: 1.1rem; margin-bottom: 2rem;'>五項技術分析 + 智能診斷 | 即時看盤</p>", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    code = st.text_input("輸入台股代號", value="2330", label_visibility="collapsed", placeholder="例如: 2360、0050、2330")
with col2:
    run = st.button("🚀 開始診斷", use_container_width=True, type="primary")

@st.cache_data(ttl=300)
def get_stock_data(ticker, period="6mo"):
    try:
        stock = yf.Ticker(f"{ticker}.TW")
        hist = stock.history(period=period)
        info = stock.info
        return hist, info
    except:
        return None, None

def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data):
    exp1 = data['calculate_macd(data):
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    return macd, signal, hist

def calculate_bollinger(data, period=20):
    ma = data['calculate_bollinger(data, period=20):
    ma = data['Close'].rolling(period).mean()
    std = data['Close'].rolling(period).std()
    upper = ma + 2 * std
    lower = ma - 2 * std
    return upper, ma, lower

if run and code:
    with st.spinner('診斷中...'):
        hist, info = get_stock_data(code)
        hist = hist.dropna(subset=['Close', 'Volume'])

        if hist is None or hist.empty or len(hist) < 20:
            st.error(f"❌ 抓不到 {code} 的有效資料，可能是代號錯誤、剛上市、或今日未交易。")
            st.info("💡 建議試試：2330 台積電、0050 元大台灣50、2454 聯發科")
        else:
            is_etf = info.get('quoteType') == 'ETF' or code.startswith('00')

            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            change = current_price - prev_price
            change_pct = (change / prev_price) * 100

            volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].rolling(20).mean().iloc[-1]
            volume_ratio = volume / avg_volume if avg_volume > 0 else 0

            rsi_series = calculate_rsi(hist)
            rsi = rsi_series.iloc[-1]
            macd, signal, hist_macd = calculate_macd(hist)

                             
            ma5 = hist['# 均線 + 布林
            ma5 = hist['Close'].rolling(5).mean().iloc[-1]
            ma20 = hist['Close'].rolling(20).mean().iloc[-1]
            ma60 = hist['Close'].rolling(60).mean().iloc[-1]
            bb_upper, bb_mid, bb_lower = calculate_bollinger(hist)
            bb_upper, bb_mid, bb_lower = bb_upper.iloc[-1], bb_mid.iloc[-1], bb_lower.iloc[-1]

            ma_trend = "多頭" if ma5 > ma20 > ma60 else "空頭" if ma5 < ma20 < ma60 else "糾結"
            ma_color = "positive" if ma_trend == "多頭" else "negative" if ma_trend == "空頭" else "neutral"

            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) * 100 if bb_upper!= bb_lower else 50
            bb_text = "上軌" if bb_position > 80 else "下軌" if bb_position < 20 else "中軌"

            st.markdown("                             
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                color_class = "### 📈 五項技術診斷")
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                color_class = "positive" if change >= 0 else "negative"
                st.markdown(f                                                                                                                                                                                                                                                                                                                                 , unsafe_allow_html=True)

            with col2:
                rsi_color = """"
                <div class="metric-card">
                    <div class="card-title">目前股價</div>
                    <div class="card-value">${current_price:.2f}</div>
                    <div class="card-delta {color_class}">{change:+.2f} ({change_pct:+.2f}%)</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                rsi_color = "negative" if rsi > 70 else "positive" if rsi < 30 else "neutral"
                rsi_text = "超買" if rsi > 70 else "超賣" if rsi < 30 else "中性"
                st.markdown(f                                                                                                                                                                                                                                                                                          , unsafe_allow_html=True)

            with col3:
                vol_color = """"
                <div class="metric-card">
                    <div class="card-title">RSI 指標</div>
                    <div class="card-value {rsi_color}">{rsi:.1f}</div>
                    <div class="card-delta">{rsi_text}</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                vol_color = "positive" if volume_ratio > 1.5 else "negative" if volume
