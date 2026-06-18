import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

# ========== 頁面設定 ==========
st.set_page_config(
    page_title="台股智能診斷 Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== Pro 版 CSS - 高對比度版 ==========
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css');

  .stApp {
        background-color: #0f172a;
    }

  .metric-card {
        background: #1e293b;
        border: 1px solid #475569;
        padding: 1.5rem;
        border-radius: 0.75rem;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
  .metric-card:hover {
        transform: translateY(-4px);
        border-color: #3b82f6;
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.4);
    }

  .card-title {
        color: #f8fafc;
        font-size: 0.875rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

  .card-value {
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 800;
        line-height: 1;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }

  .card-delta {
        color: #e2e8f0;
        font-size: 0.875rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }

  .positive { color: #22c55e!important; font-weight: 700; }
  .negative { color: #ef4444!important; font-weight: 700; }
  .neutral { color: #facc15!important; font-weight: 700; }

    h1, h2, h3, h4 {
        color: #ffffff!important;
    }

  .stTextInput > div > div > input {
        background-color: #1e293b;
        color: #ffffff;
        border: 1px solid #475569;
        font-size: 1.1rem;
    }

  .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        font-weight: 700;
        border: none;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# ========== 標題 ==========
st.markdown("# 📊 台股智能診斷系統 Pro")
st.markdown("<p style='color: #cbd5e1; font-size: 1.1rem; margin-bottom: 2rem;'>ETF 模式 + 個股技術分析 | 即時診斷</p>", unsafe_allow_html=True)

# ========== 輸入區 ==========
col1, col2 = st.columns([3, 1])
with col1:
    code = st.text_input("輸入台股代號", value="2330", label_visibility="collapsed", placeholder="例如: 2360、0050、2330")
with col2:
    run = st.button("🚀 開始診斷", use_container_width=True, type="primary")

# ========== 工具函數 ==========
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

# ========== 主程式 ==========
if run and code:
    with st.spinner('診斷中...'):
        hist, info = get_stock_data(code)

        # 防呆：檢查資料
        if hist is None or hist.empty or len(hist) < 20:
            st.error(f"❌ 抓不到 {code} 的資料，可能是代號錯誤、剛上市、或今日未交易。請換個代號試試。")
            st.info("💡 建議試試：2330 台積電、0050 元大台灣50、2454 聯發科")
        else:
            # 判斷 ETF 或個股
            is_etf = info.get('quoteType') == 'ETF' or code.startswith('00')

            # 全部改用.iloc 避免 KeyError
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

            # ========== 卡片顯示 ==========
            st.markdown("### 📈 即時診斷結果")

            col1, col2, col3, col4 = st.columns(4)

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
                    <div class="card-delta">{rsi_text}</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                vol_color = "positive" if volume_ratio > 1.5 else "negative" if volume_ratio < 0.5 else "neutral"
                vol_text = "爆量" if volume_ratio > 1.5 else "量縮" if volume_ratio < 0.5 else "均量"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="card-title">成交量</div>
                    <div class="card-value {vol_color}">{volume_ratio:.1f}x</div>
                    <div class="card-delta">{vol_text} · {int(volume/1000)}張</div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                macd_color = "positive" if hist_macd.iloc[-1] > 0 else "negative"
                macd_text = "多頭" if hist_macd.iloc[-1] > 0 else "空頭"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="card-title">MACD</div>
                    <div class="card-value {macd_color}">{hist_macd.iloc[-1]:.2f}</div>
                    <div class="card-delta">{macd_text}訊號</div>
                </div>
                """, unsafe_allow_html=True)

            # ========== 個股才顯示K線 ==========
            if not is_etf:
                st.markdown("### 📊 技術線圖")

                fig = make_subplots(
                    rows=3, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.05,
                    row_heights=[0.6, 0.2, 0.2],
                    subplot_titles=('K線圖', '成交量', 'MACD')
                )

                # K線
                fig.add_trace(go.Candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close'],
                    name='K線',
                    increasing_line_color='#22c55e',
                    decreasing_line_color='#ef4444'
                ), row=1, col=1)

                # MA線
                ma5 = hist['Close'].rolling(5).mean()
                ma20 = hist['Close'].rolling(20).mean()
                ma60 = hist['Close'].rolling(60).mean()

                fig.add_trace(go.Scatter(x=hist.index, y=ma5, name='MA5', line=dict(color='#fbbf24', width=1)), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=ma20, name='MA20', line=dict(color='#a78bfa', width=1)), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=ma60, name='MA60', line=dict(color='#60a5fa', width=1)), row=1, col=1)

                # 成交量
                colors = ['#22c55e' if hist['Close'].iloc[i] >= hist['Open'].iloc[i] else '#ef4444' for i in range(len(hist))]
                fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='成交量', marker_color=colors), row=2, col=1)

                # MACD
                fig.add_trace(go.Bar(x=hist.index, y=hist_macd, name='MACD柱', marker_color='#64748b'), row=3, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=macd, name='DIF', line=dict(color='#3b82f6', width=2)), row=3, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=signal, name='DEA', line=dict(color='#f59e0b', width=2)), row=3, col=1)

                fig.update_layout(
                    template='plotly_dark',
                    height=800,
                    showlegend=True,
                    xaxis_rangeslider_visible=False,
                    paper_bgcolor='#0f172a',
                    plot_bgcolor='#1e293b',
                    font=dict(color='#f8fafc', size=12)
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("💡 ETF 模式：專注基本指標，不顯示技術線圖")

            # ========== 診斷結論 ==========
            st.markdown("### 🎯 診斷結論")

            conclusions = []
            if rsi > 70:
                conclusions.append("RSI 超買區，短線過熱注意回調風險")
            elif rsi < 30:
                conclusions.append("RSI 超賣區，短線有反彈機會")
            else:
                conclusions.append("RSI 中性區間，多空未明")

            if volume_ratio > 1.5:
                conclusions.append("今日爆量，有主力進場跡象")
            elif volume_ratio < 0.5:
                conclusions.append("量能萎縮，市場觀望氣氛濃")

            if hist_macd.iloc[-1] > 0 and macd.iloc[-1] > signal.iloc[-1]:
                conclusions.append("MACD 多頭排列，趨勢偏強")
            elif hist_macd.iloc[-1] < 0 and macd.iloc[-1] < signal.iloc[-1]:
                conclusions.append("MACD 空頭排列，趨勢偏弱")

            for c in conclusions:
                st.markdown(f"- {c}")

else:
    st.info("👆 輸入台股代號，點擊「開始診斷」查看即時分析")

    st.markdown("### 🔥 熱門標的")
    cols = st.columns(6)
    hot_stocks = ["2330", "2454", "2317", "0050", "00878", "00929"]
    for i, stock in enumerate(hot_stocks):
        if cols[i].button(stock, key=f"hot_{stock}", use_container_width=True):
            st.session_state.code = stock
            st.rerun()
