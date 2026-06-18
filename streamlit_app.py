import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 頁面設定
st.set_page_config(
    page_title="台股智能診斷",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自訂 CSS
st.markdown("""
<style>
   .main {background-color: #0E1117;}
   .stMetric {
        background-color: #1E2329;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2B3139;
    }
   .score-card {
        background: linear-gradient(135deg, #1E2329 0%, #2B3139 100%);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #3B4252;
        text-align: center;
    }
    h1 {color: #FAFAFA; text-align: center;}
    h3 {color: #00D4AA;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>📈 台股智能診斷系統</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>ETF/個股自動切換｜五項技術評分｜拒絕當韭菜</p>", unsafe_allow_html=True)

# 輸入區
col_input, col_btn = st.columns([4,1])
with col_input:
    代號 = st.text_input(" ", placeholder="輸入台股代號，如 2330、0050、2360", label_visibility="collapsed").strip()
with col_btn:
    分析按鈕 = st.button("開始診斷", type="primary", use_container_width=True)

if 分析按鈕 and 代號:
    try:
        etf清單 = ['0050', '0056', '00878', '006208', '00692', '00713', '00919', '00929', '00940']
        是ETF = 代號 in etf清單

        股票代號 = f"{代號}.TW"
        抓取期間 = "1y" if 是ETF else "6mo"

        with st.spinner(f"正在診斷 {代號}..."):
            data = yf.download(股票代號, period=抓取期間, interval="1d", progress=False, auto_adjust=True)

        if data.empty:
            st.error("😵 抓不到資料，請確認代號正確")
            st.stop()

        開盤 = data['Open'].squeeze()
        收盤 = data['Close'].squeeze()
        最高 = data['High'].squeeze()
        最低 = data['Low'].squeeze()
        成交量 = data['Volume'].squeeze()

        # 技術指標
        ma5 = 收盤.rolling(5, min_periods=1).mean()
        ma20 = 收盤.rolling(20, min_periods=1).mean()
        ma60 = 收盤.rolling(60, min_periods=1).mean()
        ma120 = 收盤.rolling(120, min_periods=1).mean()

        delta = 收盤.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(14, min_periods=1).mean()
        avg_loss = loss.rolling(14, min_periods=1).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        最新價 = float(收盤.dropna().iloc[-1])
        昨收價 = float(收盤.dropna().iloc[-2])
        漲跌幅 = (最新價/昨收價-1)*100
        最新RSI = rsi.iloc[-1]
        最新量 = 成交量.iloc[-1]

        # 股票名稱
        try:
            ticker_info = yf.Ticker(股票代號).info
            名稱 = ticker_info.get('longName', 代號)
        except:
            名稱 = 代號

        st.markdown(f"### {名稱} ({代號}) | {'🏦 ETF模式' if 是ETF else '🎯 個股模式'}")
        st.divider()

        # 四大指標卡片
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 最新收盤", f"{最新價:.2f}", f"{漲跌幅:+.2f}%")
        col2.metric("📊 RSI(14)", f"{最新RSI:.1f}", "超買>70" if 最新RSI>70 else "超賣<30" if 最新RSI<30 else "中性")
        col3.metric("📈 成交量", f"{最新量/1000:.0f} 張", f"{最新量/成交量.rolling(20).mean().iloc[-1]:.1f}x")
        col4.metric("📅 資料範圍", data.index[0].strftime('%Y/%m/%d'), data.index[-1].strftime('%Y/%m/%d'))

        # K線圖 Plotly 版
        st.markdown("### 📉 技術線圖")
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                           vertical_spacing=0.03, row_heights=[0.7, 0.3])

        fig.add_trace(go.Candlestick(x=data.index, open=開盤, high=最高, low=最低, close=收盤,
                                     name="K線", increasing_line_color='#00D4AA', decreasing_line_color='#FF5A5F'), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=ma5, name='MA5', line=dict(color='#FFB800', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=ma20, name='MA20', line=dict(color='#00D4AA', width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=ma60, name='MA60', line=dict(color='#8B5CF6', width=1.5)), row=1, col=1)

        fig.add_trace(go.Bar(x=data.index, y=成交量, name='成交量',
                            marker_color=['#FF5A5F' if 收盤.iloc[i]<開盤.iloc[i] else '#00D4AA' for i in range(len(收盤))]),
                     row=2, col=1)

        fig.update_layout(height=600, xaxis_rangeslider_visible=False,
                         template='plotly_dark', showlegend=True,
                         paper_bgcolor='#0E1117', plot_bgcolor='#0E1117')
        fig.update_xaxes(showgrid=True, gridcolor='#2B3139')
        fig.update_yaxes(showgrid=True, gridcolor='#2B3139')
        st.plotly_chart(fig, use_container_width=True)

        # 智能評分
        st.markdown("### 🎯 五項技術評分")
        評分 = {}

        if 是ETF:
            ma120_20天前 = ma120.iloc[-20] if len(ma120) >= 20 else ma120.iloc[0]
            ma120_斜率 = (ma120.iloc[-1] - ma120_20天前) / ma120_20天前 * 100
            評分['長期趨勢'] = 20 if ma120_斜率 > 0 else 0

            乖離率 = (最新價 / ma120.iloc[-1] - 1) * 100
            評分['乖離率'] = 20 if 乖離率 < -5 else 10 if 乖離率 < 0 else 0
            評分['季線'] = 20 if 最新價 > ma60.iloc[-1] else 0
            評分['動能'] = 20 if 最新RSI < 40 else 10 if 最新RSI < 50 else 0

            量能比 = 最新量 / 成交量.rolling(20, min_periods=1).mean().iloc[-1]
            評分['籌碼安定'] = 20 if 量能比 < 1.2 and 最新價 >= 昨收價 else 10 if 量能比 < 1.5 else 0

            項目說明 = ['MA120斜率', '乖離MA120', '站上季線', 'RSI超賣', '縮量價穩']
            數值 = [f"{ma120_斜率:.2f}%", f"{乖離率:.2f}%", f"{最新價:.0f}>{ma60.iloc[-1]:.0f}", f"{最新RSI:.1f}", f"{量能比:.2f}x"]
        else:
            ma20_5天前 = ma20.iloc[-5] if len(ma20) >= 5 else ma20.iloc[0]
            ma20_斜率 = (ma20.iloc[-1] - ma20_5天前) / ma20_5天前 * 100
            評分['趨勢'] = 20 if ma20_斜率 > 1 else 10 if ma20_斜率 > 0 else 0

            量能比 = 最新量 / 成交量.rolling(20, min_periods=1).mean().iloc[-1]
            評分['量能'] = 20 if 量能比 > 1.5 and 最新價 > 昨收價 else 10 if 量能比 > 1 else 0
            評分['均線'] = 20 if 最新價 > ma20.iloc[-1] else 0
            評分['動能'] = 20 if 50 < 最新RSI < 70 else 10 if 40 < 最新RSI <= 50 else 0

            近20高 = 最高.rolling(20, min_periods=1).max().iloc[-2]
            評分['支撐壓力'] = 20 if 最新價 > 近20高 else 0

            項目說明 = ['MA20斜率', '爆量上攻', '站上月線', 'RSI強勢', '突破新高']
            數值 = [f"{ma20_斜率:.2f}%", f"{量能比:.2f}x", f"{最新價:.0f}>{ma20.iloc[-1]:.0f}", f"{最新RSI:.1f}", f"{最新價:.0f}>{近20高:.0f}"]

        總分 = sum(評分.values())

        # 分數卡片
        col_score1, col_score2, col_score3 = st.columns([1,2,1])
        with col_score2:
            if 是ETF:
                if 總分 >= 60:
                    st.success(f"## {總分} / 100 分")
                    st.markdown("<div class='score-card'><h3>🟢 適合分批存股</h3><p>長期持有，逢低加碼</p></div>", unsafe_allow_html=True)
                elif 總分 >= 40:
                    st.warning(f"## {總分} / 100 分")
                    st.markdown("<div class='score-card'><h3>🟡 價格合理</h3><p>可小額定期定額</p></div>", unsafe_allow_html=True)
                else:
                    st.error(f"## {總分} / 100 分")
                    st.markdown("<div class='score-card'><h3>🔴 價格偏高</h3><p>建議觀望等回檔</p></div>", unsafe_allow_html=True)
            else:
                if 總分 >= 60:
                    st.success(f"## {總分} / 100 分")
                    st.markdown("<div class='score-card'><h3>🟢 偏多格局</h3><p>可留意買點，設好停損</p></div>", unsafe_allow_html=True)
                elif 總分 >= 40:
                    st.warning(f"## {總分} / 100 分")
                    st.markdown("<div class='score-card'><h3>🟡 中性盤整</h3><p>觀望為主，不追高</p></div>", unsafe_allow_html=True)
                else:
                    st.error(f"## {總分} / 100 分")
                    st.markdown("<div class='score-card'><h3>🔴 偏空格局</h3><p>謹慎操作，避免抄底</p></div>", unsafe_allow_html=True)

        # 評分明細
        評分表 = pd.DataFrame({
            '項目': 項目說明,
            '得分': [f"{v}/20" for v in 評分.values()],
            '數值': 數值,
            '狀態': ['✅' if v==20 else '⚠️' if v==10 else '❌' for v in 評分.values()]
        })
        st.dataframe(評分表, hide_index=True, use_container_width=True)

    except Exception as e:
        st.error(f"😵 發生錯誤: {e}")
        st.info("可能代號錯誤或資料抓取失敗，請重試")

elif 分析按鈕:
    st.warning("⚠️ 請先輸入台股代號")
