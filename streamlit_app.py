import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import warnings
import re
warnings.filterwarnings('ignore')

st.set_page_config(page_title="台股燈號", page_icon="💡", layout="wide")

st.markdown("""
<style>
.stApp {background: #F8F3E9;}
.block-container {padding-top: 1rem; max-width: 1200px;}
* {color: #4A4A4A!important; font-family: 'Noto Sans TC', sans-serif!important; font-weight: 500!important;}
h1 {font-size: 48px!important; text-align: center!important; margin-bottom: 0!important; color: #4A4A4A!important;}
p,div,span {font-size: 20px!important;}
input[type="text"] {background: #E9D8C1!important; color: #4A4A4A!important; border: 3px solid #D6C0B7!important; font-size: 28px!important; text-align: center!important; padding: 16px!important; border-radius: 12px!important;}
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

st.markdown("<h1>💡 台股燈號 L10.23.11</h1>", unsafe_allow_html=True)

with st.expander("點我看使用說明書 & 分數算法", expanded=False):
    st.markdown("""
    ### 支援範圍
    **全部台股市場**：上市股票、上櫃股票、ETF、ETN、權證、特別股、債券ETF，只要能交易的都支援

    **代號格式**：4~6 碼英數都可
    例：`2330` 台積電、`0050` 元大50、`00403A` 統一升級50、`00679B` 元大美債20年、`00632R` 元大台灣50反1

    ### 分數怎麼算，100 分滿分
    | 指標 | 佔分 | 加分條件 |
    | --- | --- | --- |
    | **年線趨勢** | 40 | 股價 > 年線MA250 才給分 |
    | **RSI強弱** | 15 | <30超跌+15, 30-50+10, 50-70+5 |
    | **成交量** | 15 | >1.5倍爆量+15, >1.0倍+10, 量縮+5 |
    | **MACD動能** | 15 | 柱狀體>0 才給分 |
    | **短線均線** | 15 | 價>MA20>MA60 +15, 價>MA20 +10 |

    **70-100 綠燈 買進訊號｜40-69 黃燈 觀望｜0-39 紅燈 避開**

    ### 資料來源
    **全部**：Yahoo Finance，上市.TW、上櫃.TWO 自動判斷
    **興櫃**：純數字代號額外嘗試 FinMind API
    **注意**：2025年新上市商品 Yahoo 可能延遲 1-2 週更新

    **這是技術分析輔助工具，非投資建議。**
    """)

st.markdown("<p style='text-align: center; font-size: 24px;'>全市場版 | 股票ETF權證全支援</p>", unsafe_allow_html=True)

if 'current_stock' not in st.session_state:
    st.session_state.current_stock = st.query_params.get("stock", "")

hot_stocks = {
    "台積電2330":"2330", "0050":"0050", "00878":"00878",
    "統一升級50 00403A":"00403A", "元大美債20年 00679B":"00679B",
    "長榮2603":"2603", "鴻海2317":"2317", "易華電6428":"6428",
    "00940":"00940", "00919":"00919"
}
選項 = ["🔥 選擇熱門股"] + list(hot_stocks.keys())
選擇 = st.selectbox("", 選項, label_visibility="collapsed")
if 選擇!= "🔥 選擇熱門股":
    st.session_state.current_stock = hot_stocks[選擇]
    st.query_params["stock"] = hot_stocks[選擇]

st.text_input(
    "輸入台股代號",
    placeholder="例：2330、0050、00403A、00679B 全部都能查",
    key="current_stock",
    label_visibility="collapsed"
)

st.button("⚡ 開始掃描", use_container_width=True, type="primary")

@st.cache_data(ttl=3600)
def get_stock_data(stock_code):
    stock = stock_code.upper().strip()
    df = pd.DataFrame()
    市場別 = ""

    # 規則：台股全部先試.TW，上市櫃ETF都在這
    試算清單 = [f"{stock}.TW", f"{stock}.TWO"]

    for ticker in 試算清單:
        try:
            df = yf.download(ticker, period="1y", progress=False, auto_adjust=True, timeout=10)
            if not df.empty and len(df) > 5:
                市場別 = "上市/ETF" if ".TW" in ticker else "上櫃"
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                return df.dropna(), 市場別
        except:
            continue

    # 純數字代號額外試興櫃 FinMind
    if stock.isdigit():
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
            url = "https://api.finmindtrade.com/api/v4/data"
            params = {
                "dataset": "TaiwanStockPrice",
                "data_id": stock,
                "start_date": start_date,
                "end_date": end_date
            }
            res = requests.get(url, params=params, timeout=5)
            data = res.json()
            if data.get('status') == 200 and data.get('data'):
                df = pd.DataFrame(data['data'])
                df = df.rename(columns={'date':'Date','open':'Open','max':'High','min':'Low','close':'Close','Trading_Volume':'Volume'})
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.set_index('Date').sort_index()
                市場別 = "興櫃"
        except:
            pass

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df.dropna(), 市場別

def 計算指標(df):
    df['MA20'] = df['Close'].rolling(20, min_periods=1).mean()
    df['MA60'] = df['Close'].rolling(60, min_periods=1).mean()
    df['MA250'] = df['Close'].rolling(250, min_periods=1).mean()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14, min_periods=1).mean()
    loss = -delta.where(delta < 0, 0).rolling(14, min_periods=1).mean()
    rs = gain / loss.replace(0, 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))

    df['Volume_MA'] = df['Volume'].rolling(20, min_periods=1).mean().replace(0, 1)
    df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']

    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    return df.ffill()

stock = st.session_state.current_stock.strip().upper()
if stock:
    # 支援 4~6 碼英數字，涵蓋股票ETF權證
    if not re.match(r'^[0-9A-Z]{4,6}$', stock):
        st.error(f"❌ 代號錯誤：{stock}，請輸入4~6碼台股代號，例如 2330、0050、00403A")
        st.query_params.clear()
        st.stop()

    st.query_params["stock"] = stock
    with st.spinner(f"抓取 {stock} 真實數據中..."):
        df, 市場別 = get_stock_data(stock)

    if df.empty or len(df) < 5:
        st.error(f"❌ {stock} 查無資料或資料不足5天")
        st.info("💡 可能原因：1. 2025年新上市商品 Yahoo 尚未收錄 2. 代號打錯 3. 已下市\n查詢正確代號: https://isin.twse.com.tw")
        st.stop()

    st.success(f"✅ 成功抓取 {stock} {市場別} 真實數據，共{len(df)}天")
    if len(df) < 250:
        st.warning(f"⚠️ {stock} 只有{len(df)}天資料，年線會不準，但繼續分析")

    df = 計算指標(df)
    latest = df.iloc[-1]

    price = float(latest['Close'])
    ma250 = float(latest['MA250']) if not pd.isna(latest['MA250']) else 0
    ma20 = float(latest['MA20'])
    ma60 = float(latest['MA60'])
    rsi = float(latest['RSI']) if not pd.isna(latest['RSI']) else 50
    vol_ratio = float(latest['Volume_Ratio']) if not pd.isna(latest['Volume_Ratio']) else 1
    macd_hist = float(latest['MACD_Hist']) if not pd.isna(latest['MACD_Hist']) else 0

    年線上方 = price > ma250 if ma250 > 0 else False
    總分, 分析, 顏色 = 0, [], []

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
    for i, (文案, 卡片顏色) in enumerate(zip(分析, 顏色)):
        with cols[i]:
            st.markdown(f'<div class="card-box card-{卡片顏色}">{文案}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader(f"📈 {stock} {市場別} K線圖")

    df_plot = df.tail(250).copy()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])

    fig.add_trace(go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'],
                                 increasing_line_color='#E88C8C', decreasing_line_color='#8CB88C', name='K線'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MA20'], line=dict(color='#D6C07C', width=1), name='MA20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MA60'], line=dict(color='#8CB88C', width=1), name='MA60'), row=1, col=1)
    if ma250 > 0:
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MA250'], line=dict(color='#4A4A4A', width=2), name='年線'), row=1, col=1)

    colors = ['#E88C8C' if row['Open'] > row['Close'] else '#8CB88C' for _, row in df_plot.iterrows()]
    fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['Volume'], marker_color=colors, name='成交量'), row=2, col=1)

    fig.update_layout(xaxis_rangeslider_visible=False, height=600, showlegend=True,
                      plot_bgcolor='#F8F3E9', paper_bgcolor='#F8F3E9', font=dict(color='#4A4A4A'))
    fig.update_yaxes(title_text="股價", row=1, col=1)
    fig.update_yaxes(title_text="成交量", row=2, col=1)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔍 數據驗證表")
    驗證表 = df.tail(5)[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    驗證表.index = 驗證表.index.strftime('%Y-%m-%d')
    st.dataframe(驗證表, use_container_width=True)
