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
.score-box {
        background: #1e293b; border: 2px solid #475569;
        padding: 2rem; border-radius: 1rem; text-align: center;
    }
.score-num { font-size: 4rem; font-weight: 900; line-height: 1; }
.score-label { font-size: 1.2rem; font-weight: 600; margin-top: 0.5rem; }
.score-high { border-color: #22c55e; color: #22c55e; }
.score-mid { border-color: #facc15; color: #facc15; }
.score-low { border-color: #ef4444; color: #ef4444; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 📊 台股智能診斷系統 Pro")
st.markdown("<p style='color: #cbd5e1; font-size: 1.1rem; margin-bottom: 2rem;'>五項技術分析 + 智能診斷評分 | 即時看盤</p>", unsafe_allow_html=True)

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
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    return macd, signal, hist

def calculate_bollinger(data, period=20):
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

            ma5 = hist['Close'].rolling(5).mean().iloc[-1]
            ma20 = hist['Close'].rolling(20).mean().iloc[-1]
            ma60 = hist['Close'].rolling(60).mean().iloc[-1]
            bb_upper, bb_mid, bb_lower = calculate_bollinger(hist)
            bb_upper, bb_mid, bb_lower = bb_upper.iloc[-1], bb_mid.iloc[-1], bb_lower.iloc[-1]

            ma_trend = "多頭" if ma5 > ma20 > ma60 else "空頭" if ma5 < ma20 < ma60 else "糾結"
            ma_color = "positive" if ma_trend == "多頭" else "negative" if ma_trend == "空頭" else "neutral"

            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) * 100 if bb_upper!= bb_lower else 50
            bb_text = "上軌" if bb_position > 80 else "下軌" if bb_position < 20 else "中軌"

            # ========== 評分系統 ==========
            score = 0
            # RSI評分 0-20分
            if rsi < 30: score += 20
            elif rsi < 40: score += 15
            elif rsi < 60: score += 10
            elif rsi < 70: score += 5

            # MACD評分 0-20分
            if hist_macd.iloc[-1] > 0 and macd.iloc[-1] > signal.iloc[-1]: score += 20
            elif hist_macd.iloc[-1] > 0: score += 10

            # 量能評分 0-20分
            if volume_ratio > 1.5: score += 20
            elif volume_ratio > 1.0: score += 15
            elif volume_ratio > 0.8: score += 10
            else: score += 5

            # 均線評分 0-20分
            if ma_trend == "多頭": score += 20
            elif ma_trend == "糾結": score += 10

            # 布林評分 0-20分
            if 20 < bb_position < 80: score += 20
            elif bb_position < 20: score += 15
            else: score += 5

            score_class = "score-high" if score >= 70 else "score-mid" if score >= 40 else "score-low"
            score_text = "強勢買進" if score >= 80 else "偏多觀察" if score >= 60 else "中性觀望" if score >= 40 else "偏空小心" if score >= 20 else "空頭風險"

            st.markdown("### 🎯 診斷總評分")
            st.markdown(f"""
            <div class="score-box {score_class}">
                <div class="score-num">{score}</div>
                <div class="score-label">{score_text}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 📈 五項技術診斷")
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                color_class = "positive" if change >= 0 else "negative"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="card-title">目前股價</div>
                    <div class="card-value">${current_price:.2f}</div>
                    <div class="card-delta {color_class}">{change:+.2f} ({change_pct:+.2f}%)</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                rsi_color = "negative" if rsi > 70 else "positive" if rsi < 30 else "neutral"
                rsi_text = "超買" if rsi > 70 else "超賣" if rsi < 30 else "中性"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="card-title">RSI 指標</div>
                    <div class="card-value {rsi_color}">{rsi:.1f}</div>
                    <div class="card-delta">{rsi_text} | {20 if rsi<30 else 15 if rsi<40 else 10 if rsi<60 else 5 if rsi<70 else 0}分</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                vol_color = "positive" if volume_ratio > 1.5 else "negative" if volume_ratio < 0.5 else "neutral"
                vol_text = "爆量" if volume_ratio > 1.5 else "量縮" if volume_ratio < 0.5 else "均量"
                vol_score = 20 if volume_ratio > 1.5 else 15 if volume_ratio > 1.0 else 10 if volume_ratio > 0.8 else 5
                st.markdown(f"""
                <div class="metric-card">
                    <div class="card-title">成交量</div>
                    <div class="card-value {vol_color}">{volume_ratio:.1f}x</div>
                    <div class="card-delta">{vol_text} | {vol_score}分</div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                macd_color = "positive" if hist_macd.iloc[-1] > 0 else "negative"
                macd_text = "多頭" if hist_macd.iloc[-1] > 0 else "空頭"
                macd_score = 20 if hist_macd.iloc[-1] > 0 and macd.iloc[-1] > signal.iloc[-1] else 10 if hist_macd.iloc[-1] > 0 else 0
                st.markdown(f"""
                <div class="metric-card">
                    <div class="card-title">MACD</div>
                    <div class="card-value {macd_color}">{hist_macd.iloc[-1]:.2f}</div>
                    <div class="card-delta">{macd_text} | {macd_score}分</div>
                </div>
                """, unsafe_allow_html=True)

            with col5:
                ma_score = 20 if ma_trend == "多頭" else 10 if ma_trend == "糾結" else 0
                bb_score = 20 if 20 < bb_position < 80 else 15 if bb_position < 20 else 5
                st.markdown(f"""
                <div class="metric-card">
                    <div class="card-title">均線+布林</div>
                    <div class="card-value {ma_color}">{ma_trend}</div>
                    <div class="card-delta">布林{bb_text} | {ma_score+bb_score}分</div>
                </div>
                """, unsafe_allow_html=True)

            if not is_etf:
                st.markdown("### 📊 技術線圖")
                fig = make_subplots(
                    rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                    row_heights=[0.7, 0.15, 0.15],
                    subplot_titles=('K線圖 + MA均線 + 布林通道', '成交量', 'MACD')
                )
                fig.add_trace(go.Candlestick(
                    x=hist.index, open=hist['Open'], high=hist['High'],
                    low=hist['Low'], close=hist['Close'], name='K線',
                    increasing_line_color='#22c55e', decreasing_line_color='#ef4444'
                ), row=1, col=1)

                ma5_series = hist['Close'].rolling(5).mean()
                ma20_series = hist['Close'].rolling(20).mean()
                ma60_series = hist['Close'].rolling(60).mean()
                fig.add_trace(go.Scatter(x=hist.index, y=ma5_series, name='MA5', line=dict(color='#fbbf24', width=1.5)), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=ma20_series, name='MA20', line=dict(color='#a78bfa', width=1.5)), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=ma60_series, name='MA60', line=dict(color='#60a5fa', width=1.5)), row=1, col=1)

                bb_upper_s, bb_mid_s, bb_lower_s = calculate_bollinger(hist)
                fig.add_trace(go.Scatter(x=hist.index, y=bb_upper_s, name='布林上軌', line=dict(color='#64748b', width=1, dash='dot')), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=bb_mid_s, name='布林中軌', line=dict(color='#64748b', width=1, dash='dot')), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=bb_lower_s, name='布林下軌', line=dict(color='#64748b', width=1, dash='dot'), fill='tonexty', fillcolor='rgba(100,116,139,0.1)'), row=1, col=1)

                colors = ['#22c55e' if hist['Close'].iloc[i] >= hist['Open'].iloc[i] else '#ef4444' for i in range(len(hist))]
                fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='成交量', marker_color=colors), row=2, col=1)

                fig.add_trace(go.Bar(x=hist.index, y=hist_macd, name='MACD柱', marker_color='#64748b'), row=3, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=macd, name='DIF', line=dict(color='#3b82f6', width=2)), row=3, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=signal, name='DEA', line=dict(color='#f59e0b', width=2)), row=3, col=1)

                fig.update_layout(
                    template='plotly_dark', height=1000, showlegend=True,
                    xaxis_rangeslider_visible=False, paper_bgcolor='#0f172a',
                    plot_bgcolor='#1e293b', font=dict(color='#f8fafc', size=12),
                    hovermode='x unified'
                )
                fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='#334155')
                fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='#334155')

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("💡 ETF 模式：專注基本指標，不顯示技術線圖")
else:
    st.info("👆 輸入台股代號，點擊「開始診斷」查看即時分析")
    st.markdown("### 🔥 熱門標的")
    cols = st.columns(6)
    hot_stocks = ["2330", "2454", "2317", "0050", "00878", "00929"]
    for i, stock in enumerate(hot_stocks):
        if cols[i].button(stock, key=f"hot_{stock}", use_container_width=True):
            st.session_state.code = stock
            st.rerun()
