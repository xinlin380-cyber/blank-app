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
html, body, [class*="css"] {
    font-family: 'Noto Sans TC', 'Microsoft JhengHei', 'Segoe UI Emoji', 'Apple Color Emoji', sans-serif!important;
    line-height: 2.0!important;
    font-weight: 400!important;
}
h1 {
    font-size: 48px!important;
    text-align: center!important;
    margin-bottom: 0.5rem!important;
    color: #4A4A4A!important;
    font-weight: 700!important;
    line-height: 1.4!important;
}
p, div, span, label,.stSelectbox,.stTextInput, li {
    font-size: 18px!important;
    color: #4A4A4A!important;
}
[data-testid="stExpander"] details {
    border: 2px solid #D6C0B7!important;
    border-radius: 12px!important;
    background: #E9D8C1!important;
}
[data-testid="stExpander"] details summary p {
    font-size: 18px!important;
    font-weight: 500!important;
    line-height: 2.0!important;
}
input[type="text"] {
    background: #E9D8C1!important;
    color: #4A4A4A!important;
    border: 3px solid #D6C0B7!important;
    font-size: 28px!important;
    text-align: center!important;
    padding: 16px!important;
    border-radius: 12px!important;
    line-height: 1.4!important;
}
.light-box {padding: 50px; border-radius: 25px; text-align: center; margin: 35px 0; border: 8px solid;}
.light-green {border-color: #8CB88C; background: #D6C0B7;}
.light-yellow {border-color: #D6C07C; background: #D6C0B7;}
.light-red {border-color: #E88C8C; background: #D6C0B7;}
.score-big {font-size: 120px; font-weight: 700; margin: 0; color: #FFFFFF!important; line-height: 1;}
.title-big {font-size: 70px; font-weight: 700; margin: 15px 0; color: #FFFFFF!important;}
.type-tag {font-size: 24px!important; color: #FFFFFF!important; margin-top: 10px;}
.card-box {padding: 30px 15px; border-radius: 18px; margin: 12px 0; border: 4px solid; text-align: center; min-height: 180px; background: #E9D8C1;}
.card-green {border-color: #8CB88C;}
.card-yellow {border-color: #D6C07C;}
.card-red {border-color: #E88C8C;}
.card-box * {color: #4A4A4A!important; font-size: 22px!important; font-weight: 700!important; line-height: 1.5!important;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>💡 台股燈號 L10.23.19</h1>", unsafe_allow_html=True)

with st.expander("📖 點我看完整使用說明書，新手必讀", expanded=False):
    st.markdown("### 🚀 怎麼用，3 步驟超簡單")
    st.markdown("")
    st.markdown("**1. 輸入代號**：打 4~6 碼股票代號，如 `2330` 台積電、`0050` 元大台灣50，按 Enter 就跑")
    st.markdown("")
    st.markdown("**2. 熱門股**：點上方「🔥選擇熱門股」直接選，不用記代號")
    st.markdown("")
    st.markdown("**3. 看結果**：大數字是總分 0-100 分。綠色可以買、黃色再看看、紅色先不要碰")
    st.markdown("")
    st.markdown("---")
    st.markdown("")
    st.markdown("### 📚 名詞解釋")
    st.markdown("")
    st.markdown("**🐮 上漲趨勢 / 大家在買**:多頭。股價比過去250天平均還高，代表最近買的人多，大家看好")
    st.markdown("")
    st.markdown("**🐻 下跌趨勢 / 大家在賣**：空頭。股價比過去250天平均還低，代表最近賣的人多，大家看壞")
    st.markdown("")
    st.markdown("**年線**：過去250個交易日的平均股價。站上=長期往上走，跌破=長期往下走")
    st.markdown("")
    st.markdown("**RSI 強弱指標**：看這支股票最近有沒有漲太多或跌太多")
    st.markdown("→ 數字 <30：跌過頭了，可能會反彈")
    st.markdown("→ 數字 30-70：正常範圍")
    st.markdown("→ 數字 >70：漲過頭了，可能會回檔")
    st.markdown("")
    st.markdown("**MACD 動能**：看這支股票現在有沒有力氣繼續漲")
    st.markdown("→ 正數：有力氣，比較會漲")
    st.markdown("→ 負數：沒力氣，比較會跌")
    st.markdown("")
    st.markdown("**爆量**：今天很多人買賣，成交量是平常的1.5倍以上。通常大戶進場了")
    st.markdown("")
    st.markdown("**量縮**：今天沒什麼人買賣，成交量比平常少。大家在觀望")
    st.markdown("")
    st.markdown("**短期均線**：20天和60天的平均股價。股價在兩條線上面=短期走勢強")
    st.markdown("")
    st.markdown("---")
    st.markdown("")
    st.markdown("### 🎯 為什麼不同股票分數標準不一樣？")
    st.markdown("")
    st.markdown("**📊 個股**：台積電、長榮這種公司股。看長期趨勢最重要，所以年線佔40分")
    st.markdown("")
    st.markdown("**📈 一般ETF**：0050、00878這種。跟大盤走，看長期趨勢+動能，年線佔50分")
    st.markdown("")
    st.markdown("**⚡ 槓桿ETF**：00632R這種放大版。適合短線，看動能最重要，MACD佔25分")
    st.markdown("")
    st.markdown("**💰 債券ETF**：00679B這種。債券沒什麼人在炒，成交量不重要，所以不看量")
    st.markdown("")
    st.markdown("**🎰 權證**：賭博性質。漲跌很快，所以看短期超買超賣，RSI佔30分")
    st.markdown("")
    st.markdown("---")
    st.markdown("")
    st.markdown("### 📊 燈號怎麼看")
    st.markdown("")
    st.markdown("**🟢 70-100 分 綠燈**：技術面全部轉好，買的人多，可以考慮進場")
    st.markdown("")
    st.markdown("**🟡 40-69 分 黃燈**：好壞參半，有人買有人賣，先觀望等方向明確")
    st.markdown("")
    st.markdown("**🔴 0-39 分 紅燈**：技術面偏弱，賣的人多，先避開不要接刀")
    st.markdown("")
    st.markdown("---")
    st.markdown("")
    st.markdown("### ⚠️ 重要提醒")
    st.markdown("")
    st.markdown("1. **新上市商品**：2025年新ETF如00403A，資料可能不滿250天，年線會不準")
    st.markdown("")
    st.markdown("2. **這不是明牌**：只是技術分析工具，幫你看現在買氣強不強。投資一定有風險")
    st.markdown("")
    st.markdown("3. **不要All in**：就算綠燈也分批買，黃燈紅燈就先不要碰")
    st.markdown("")
    st.markdown("**資料來源**：Yahoo Finance 免費公開資料")

st.markdown("<p style='text-align: center; font-size: 20px;'>✨ 白話文版｜新手友善✨</p>", unsafe_allow_html=True)

if 'current_stock' not in st.session_state:
    st.session_state.current_stock = st.query_params.get("stock", "")

hot_stocks = {
    "台積電2330":"2330", "0050":"0050", "00878":"00878",
    "統一升級50 00403A":"00403A", "元大美債20年 00679B":"00679B",
    "元大台灣50反1 00632R":"00632R", "長榮2603":"2603", "鴻海2317":"2317"
}
選項 = ["🔥 選擇熱門股"] + list(hot_stocks.keys())
選擇 = st.selectbox("", 選項, label_visibility="collapsed")
if 選擇!= "🔥 選擇熱門股":
    st.session_state.current_stock = hot_stocks[選擇]
    st.query_params["stock"] = hot_stocks[選擇]

st.text_input(
    "輸入台股代號",
    placeholder="例：2330、0050、00403A、00679B、00632R",
    key="current_stock",
    label_visibility="collapsed"
)

st.button("⚡ 開始掃描", use_container_width=True, type="primary")

def 判斷類型(stock_code):
    code = stock_code.upper()
    if len(code) == 6 and code.isdigit() and code.startswith('03'):
        return "🎰 權證", {"年線":20, "RSI":30, "量":20, "MACD":15, "均線":15}
    if code.endswith('B'):
        return "💰 債券ETF", {"年線":60, "RSI":10, "量":0, "MACD":15, "均線":15}
    if code.endswith('R') or code.endswith('L'):
        return "⚡ 槓桿反向ETF", {"年線":30, "RSI":20, "量":10, "MACD":25, "均線":15}
    if len(code) == 5 or (len(code) == 4 and not code.isdigit()):
        return "📈 一般ETF", {"年線":50, "RSI":10, "量":5, "MACD":20, "均線":15}
    return "📊 個股", {"年線":40, "RSI":15, "量":15, "MACD":15, "均線":15}

@st.cache_data(ttl=3600)
def get_stock_data(stock_code):
    stock = stock_code.upper().strip()
    df = pd.DataFrame()
    市場別 = ""

    試算清單 = [f"{stock}.TW", f"{stock}.TWO"]

    for ticker in 試算清單:
        try:
            df = yf.download(ticker, period="1y", progress=False, auto_adjust=True, timeout=10)
            if not df.empty and len(df) > 5:
                市場別 = "上市" if ".TW" in ticker else "上櫃"
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                return df.dropna(), 市場別
        except:
            continue

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
    if not re.match(r'^[0-9A-Z]{4,6}$', stock):
        st.error(f"❌ 代號錯誤：{stock}，請輸入4~6碼台股代號")
        st.query_params.clear()
        st.stop()

    st.query_params["stock"] = stock
    類型, 權重 = 判斷類型(stock)

    with st.spinner(f"⚡ 抓取 {stock} 真實數據中..."):
        df, 市場別 = get_stock_data(stock)

    if df.empty or len(df) < 5:
        st.error(f"❌ {stock} 查無資料或資料不足5天")
        st.info("💡 可能原因：1. 2025年新上市商品 Yahoo 尚未收錄 2. 代號打錯 3. 已下市")
        st.stop()

    st.success(f"✅ 成功抓取 {stock} {市場別} 真實數據，共{len(df)}天｜類型：{類型}")
    if len(df) < 250:
        st.warning(f"⚠️ {stock} 只有{len(df)}天資料，長期趨勢會不準，但繼續分析")

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
        加分 = 權重["年線"]
        總分 += 加分
        分析.append(f"🐮 趨勢向上<br>+{加分}分<br>比長期平均高")
        顏色.append("green")
    else:
        分析.append(f"🐻 趨勢向下<br>+0分<br>比長期平均低")
        顏色.append("red")

    if rsi < 30:
        加分 = 權重["RSI"]
        總分 += 加分
        分析.append(f"📊 跌過頭<br>+{加分}分<br>可能反彈")
        顏色.append("green")
    elif rsi < 50:
        加分 = int(權重["RSI"] * 0.67)
        總分 += 加分
        分析.append(f"📊 強弱中性<br>+{加分}分<br>正常範圍")
        顏色.append("yellow")
    elif rsi < 70:
        加分 = int(權重["RSI"] * 0.33)
        總分 += 加分
        分析.append(f"📊 漲偏高<br>+{加分}分<br>小心回檔")
        顏色.append("yellow")
    else:
        分析.append(f"📊 漲過頭<br>+0分<br>風險高")
        顏色.append("red")

    if 權重["量"] > 0:
        if vol_ratio > 1.5:
            加分 = 權重["量"]
            總分 += 加分
            分析.append(f"📈 大家在買<br>+{加分}分<br>量是平常{vol_ratio:.1f}倍")
            顏色.append("green")
        elif vol_ratio > 1.0:
            加分 = int(權重["量"] * 0.67)
            總分 += 加分
            分析.append(f"📈 買氣正常<br>+{加分}分<br>量是平常{vol_ratio:.1f}倍")
            顏色.append("yellow")
        else:
            加分 = int(權重["量"] * 0.33)
            總分 += 加分
            分析.append(f"📈 沒人買賣<br>+{加分}分<br>量是平常{vol_ratio:.1f}倍")
            顏色.append("red")
    else:
        分析.append(f"📈 成交量<br>不重要<br>+0分")
        顏色.append("yellow")

    if macd_hist > 0:
        加分 = 權重["MACD"]
        總分 += 加分
        分析.append(f"📉 有力氣漲<br>+{加分}分")
        顏色.append("green")
    else:
        分析.append(f"📉 沒力氣漲<br>+0分")
        顏色.append("red")

    if price > ma20 > ma60:
        加分 = 權重["均線"]
        總分 += 加分
        分析.append(f"🚀 短期很強<br>+{加分}分")
        顏色.append("green")
    elif price > ma20:
        加分 = int(權重["均線"] * 0.67)
        總分 += 加分
        分析.append(f"🚀 短期偏強<br>+{加分}分")
        顏色.append("yellow")
    else:
        分析.append(f"🚀 短期偏弱<br>+0分")
        顏色.append("red")

    if 總分 >= 70:
        邊框, 建議 = "light-green", "🟢 綠燈 可以買"
    elif 總分 >= 40:
        邊框, 建議 = "light-yellow", "🟡 黃燈 先看看"
    else:
        邊框, 建議 = "light-red", "🔴 紅燈 不要碰"

    st.markdown(f'<div class="light-box {邊框}"><div class="score-big">{總分}</div><div class="title-big">{建議}</div><div class="type-tag">類型：{類型}</div></div>', unsafe_allow_html=True)

    cols = st.columns(5)
    for i, (文案, 卡片顏色) in enumerate(zip(分析, 顏色)):
        with cols[i]:
            st.markdown(f'<div class="card-box card-{卡片顏色}">{文案}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader(f"📊 {stock} {市場別} K線圖")

    df_plot = df.tail(250).copy()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])

    fig.add_trace(go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'],
                                 increasing_line_color='#E88C8C', decreasing_line_color='#8CB88C', name='K線'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MA20'], line=dict(color='#D6C07C', width=1), name='20日線'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MA60'], line=dict(color='#8CB88C', width=1), name='60日線'), row=1, col=1)
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
