import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="台股燈號", page_icon="💡", layout="wide")

st.markdown("""
<style>
.stApp {background: #F8F3E9;}
.block-container {padding-top: 1rem; max-width: 1200px;}
* {color: #4A4A4A!important; font-family: 'Noto Sans TC', sans-serif!important; font-weight: 500!important;}
h1 {font-size: 48px!important; text-align: center!important; margin-bottom: 0!important; color: #4A4A4A!important;}
p,div,span {font-size: 20px!important;}
input[type="text"] {background: #E9D8C1!important; color: #4A4A4A!important; border: 3px solid #D6C0B7!important; font-size: 28px!important; text-align: center!important; padding: 16px!important; border-radius: 12px!important;}
.hot-wrap {text-align: center; margin: 25px 0;}
.hot-tag {display: inline-block; background: #D6C0B7; border: 3px solid #C9B7A7; color: #4A4A4A!important; padding: 12px 24px; margin: 8px; border-radius: 15px; font-size: 22px!important; text-decoration: none!important; cursor: pointer;}
.hot-tag:hover {background: #C9B7A7;}
.light-box {padding: 50px; border-radius: 25px; text-align: center; margin: 35px 0; border: 8px solid;}
.light-green {border-color: #8CB88C; background: #D6C0B7;}
.light-yellow {border-color: #D6C07C; background: #D6C0B7;}
.light-red {border-color: #E88C8C; background: #D6C0B7;}
.score-big {font-size: 120px; font-weight: 700; margin: 0; color: #FFFFFF!important; line-height: 1;}
.title-big {font-size: 70px; font-weight: 700; margin: 15px 0; color: #FFFFFF!important;}
.card-box {padding: 30px 15px; border-radius: 18px; margin: 12px 0; border: 4px solid; text-align: center; min-height: 180px; background: #E9D8C1;}
.card-green {border-color: #8CB88C;}
.card-yellow {border-color: #D6C07C;}
.card-red {border-color: #E88C8C;}
.card-box * {color: #4A4A4A!important; font-size: 24px!important; font-weight: 700!important; line-height: 1.5!important;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>💡 台股燈號 L10.21</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 24px;'>最終穩定版 | 任意股票+K線+不跳頁</p>", unsafe_allow_html=True)

if 'stock_code' not in st.session_state:
    st.session_state.stock_code = st.query_params.get("stock", "")

def set_stock(code):
    st.session_state.stock_code = code
    st.query_params["stock"] = code

# 熱門標籤
cols = st.columns(5)
hot_stocks = {"台積電2330":"2330", "0050":"0050", "00878":"00878", "長榮2603":"2603", "鴻海2317":"2317"}
for i, (name, code) in enumerate(hot_stocks.items()):
    with cols[i]:
        if st.button(name, key=f"hot_{code}", use_container_width=True):
            set_stock(code)
            st.rerun()

# 輸入框
def run_scan():
    st.session_state.stock_code = st.session_state.input_box
    st.query_params["stock"] = st.session_state.input_box

st.text_input(
    "輸入任意台股代號",
    placeholder="例如：2330、00940、00919、2603",
    key="input_box",
    value=st.session_state.stock_code,
    on_change=run_scan,
    label_visibility="collapsed"
)

if st.button("⚡ 開始掃描", use_container_width=True, type="primary"):
    run_scan()
    st.rerun()

# 執行掃描
if st.session_state.stock_code:
    stock = st.session_state.stock_code.replace('.TW','')
    with st.spinner(f"從Yahoo抓取 {stock} 真實數據中..."):
        try:
            ticker = f"{stock}.TW"
            df = yf.download(ticker, period="1y", progress=False, auto_adjust=True)
            if df.empty:
                st.error(f"❌ Yahoo查無 {stock}，確認代號是否正確")
                st.stop()
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.dropna()
        except Exception as e:
            st.error(f"❌ Yahoo抓取失敗：{e}")
            st.stop()

    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA60'] = df['Close'].rolling(60).mean()
    df['MA250'] = df['Close'].rolling(250).mean()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df['Volume_MA'] = df['Volume'].rolling(20).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
    ema12 = df['Close'].ewm(span=12).mean()
    ema26 = df['Close'].ewm(span=26).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    df = df.dropna()

    latest = df.iloc[-1]
    price = float(latest['Close'])
    ma250 = float(latest['MA250']) if not pd.isna(latest['MA250']) else 0
    ma20 = float(latest['MA20'])
    ma60 = float(latest['MA60'])
    rsi = float(latest['RSI'])
    vol_ratio = float(latest['Volume_Ratio'])
    macd_hist = float(latest['MACD_Hist'])

    年線上方 = price > ma250 if ma250 > 0 else False
    總分 = 0
    分析 = []
    顏色 = []

    if 年線上方:
        總分 += 40
        分析.append(f"🐮 大多頭<br>+40分<br>股價{price:.2f}>年線{ma250:.2f}")
        顏色.append("green")
    else:
        分析.append(f"🐻 空頭<br>+0分<br>股價{price:.2f}<年線{ma250:.2f}")
        顏色.append("red")

    if rsi < 30:
        總分 += 15
        分析.append(f"📊 RSI {rsi:.0f}<br>超跌<br>+15分")
        顏色.append("green")
    elif rsi < 50:
        總分 += 10
        分析.append(f"📊 RSI {rsi:.0f}<br>中性<br>+10分")
        顏色.append("yellow")
    elif rsi < 70:
        總分 += 5
        分析.append(f"📊 RSI {rsi:.0f}<br>偏高<br>+5分")
        顏色.append("yellow")
    else:
        分析.append(f"📊 RSI {rsi:.0f}<br>超買<br>+0分")
        顏色.append("red")

    if vol_ratio > 1.5:
        總分 += 15
        分析.append(f"📈 量 {vol_ratio:.1f}倍<br>爆量<br>+15分")
        顏色.append("green")
    elif vol_ratio > 1.0:
        總分 += 10
        分析.append(f"📈 量 {vol_ratio:.1f}倍<br>正常<br>+10分")
        顏色.append("yellow")
    else:
        總分 += 5
        分析.append(f"📈 量 {vol_ratio:.1f}倍<br>量縮<br>+5分")
        顏色.append("red")

    if macd_hist > 0:
        總分 += 15
        分析.append(f"📉 MACD正<br>+15分")
        顏色.append("green")
    else:
        分析.append(f"📉 MACD負<br>+0分")
        顏色.append("red")

    if price > ma20 > ma60:
        總分 += 15
        分析.append(f"🚀 短多頭<br>+15分")
        顏色.append("green")
    elif price > ma20:
        總分 += 10
        分析.append(f"🚀 偏多<br>+10分")
        顏色.append("yellow")
    else:
        分析.append(f"🚀 偏空<br>+0分")
        顏色.append("red")

    if 總分 >= 70:
        邊框, 建議 = "light-green", "綠燈 買進訊號"
    elif 總分 >= 40:
        邊框, 建議 = "light-yellow", "黃燈 觀望"
    else:
        邊框, 建議 = "light-red", "紅燈 避開"

    st.markdown(f'<div class="light-box {邊框}"><div class="score-big">{總分}</div><div class="title-big">{建議}</div></div>', unsafe_allow_html=True)

    cols = st.columns(5)
    for i, (文, 色) in enumerate(zip(分析, 顏色)):
        with cols[i]:
            st.markdown(f'<div class="card-box card-{色}">{文}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### 📊 {stock} K線圖")
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='K線', increasing_line_color='#8CB88C', decreasing_line_color='#E88C8C'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='#6D5A50', width=1), name='MA20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], line=dict(color='#D6C07C', width=1), name='MA60'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA250'], line=dict(color='#E88C8C', width=2), name='年線'), row=1, col=1)
    colors = ['#8CB88C' if row['Close'] >= row['Open'] else '#E88C8C' for _, row in df.iterrows()]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name='成交量'), row=2, col=1)
    fig.update_layout(plot_bgcolor='#F8F3E9', paper_bgcolor='#F8F3E9', font=dict(color='#4A4A4A'), xaxis_rangeslider_visible=False, height=600, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_xaxes(gridcolor='#E9D8C1')
    fig.update_yaxes(gridcolor='#E9D8C1')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🔍 Yahoo原始數據驗證")
    st.write(f"**股票**: {stock}.TW | **日期**: {df.index[-1].strftime('%Y-%m-%d')}")
    st.dataframe(df[['Open','High','Low','Close','Volume']].tail(10).round(2), use_container_width=True)
else:
    st.info("👆 輸入任意台股代號，例如：2330、00940、00919、2603")
