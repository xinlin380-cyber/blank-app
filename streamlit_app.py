import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="台股燈號", page_icon="💡", layout="wide")

st.markdown("""
<style>
.stApp {background: #000000;}
.block-container {padding-top: 1rem; max-width: 1200px;}

* {
    color: #FFFFFF!important;
    font-family: 'Noto Sans TC', sans-serif!important;
    font-weight: 900!important;
}
h1 {font-size: 52px!important; text-align: center!important; margin-bottom: 0!important;}
p,div,span {font-size: 22px!important;}

input[type="text"] {
    background: #1A1A1A!important;
    color: #FFFFFF!important;
    border: 5px solid #00FF88!important;
    font-size: 30px!important;
    text-align: center!important;
    padding: 18px!important;
    border-radius: 12px!important;
}

.hot-wrap {text-align: center; margin: 25px 0;}
.hot-tag {
    display: inline-block;
    background: #1A1A1A;
    border: 4px solid #00FF88;
    color: #FFFFFF!important;
    padding: 14px 28px;
    margin: 8px;
    border-radius: 15px;
    font-size: 24px!important;
    text-decoration: none!important;
}
.hot-tag:hover {background: #00FF88; color: #000000!important;}

.scan-btn {
    display: block; width: 100%; background: #00FF88!important;
    color: #000000!important; border: none; padding: 22px;
    font-size: 32px!important; font-weight: 900!important;
    border-radius: 15px; text-align: center; text-decoration: none!important; margin: 25px 0;
}

.light-box {
    padding: 60px; border-radius: 25px; text-align: center; margin: 35px 0;
    border: 10px solid;
}
.light-green {border-color: #00FF88; background: #001A00;}
.light-yellow {border-color: #FFDD00; background: #1A1A00;}
.light-red {border-color: #FF3366; background: #1A0000;}

.score-big {font-size: 140px; font-weight: 900; margin: 0; color: #FFFFFF!important; line-height: 1;}
.title-big {font-size: 80px; font-weight: 900; margin: 15px 0; color: #FFFFFF!important;}

.card-box {
    padding: 35px 15px; border-radius: 18px; margin: 12px 0;
    border: 6px solid; text-align: center; min-height: 180px;
}
.card-green {border-color: #00FF88; background: #002200;}
.card-yellow {border-color: #FFDD00; background: #222200;}
.card-red {border-color: #FF3366; background: #220000;}

.card-box * {
    color: #FFFFFF!important;
    font-size: 26px!important;
    font-weight: 900!important;
    line-height: 1.5!important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>💡 台股燈號 L10.10</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 26px;'>最終完整版 | 00878已修正確</p>", unsafe_allow_html=True)

query_params = st.query_params
selected_stock = query_params.get("stock", "")

hot_html = '<div class="hot-wrap">🔥 熱門：'
for name, code in {"台積電2330":"2330", "0050":"0050", "00878":"00878", "長榮2603":"2603", "鴻海2317":"2317"}.items():
    hot_html += f'<a href="?stock={code}" class="hot-tag">{name}</a>'
hot_html += '</div>'
st.markdown(hot_html, unsafe_allow_html=True)

stock = st.text_input("", value=selected_stock, placeholder="輸入代號或點上方熱門", label_visibility="collapsed")

if stock:
    st.markdown(f'<a href="?stock={stock}&scan=1" class="scan-btn">⚡ 開始掃描 {stock}</a>', unsafe_allow_html=True)

if stock and query_params.get("scan") == "1":
    with st.spinner("掃描中..."):
        try:
            ticker = f"{stock}.TW" if not stock.endswith('.TW') else stock
            df = yf.download(ticker, period="2y", progress=False)
            if df.empty:
                st.error("❌ 查無此股票")
                st.stop()
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.dropna()
        except Exception as e:
            st.error(f"❌ 錯誤：{e}")
            st.stop()

    # 計算指標
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
    ma250 = float(latest['MA250'])
    ma20 = float(latest['MA20'])
    ma60 = float(latest['MA60'])
    rsi = float(latest['RSI'])
    vol_ratio = float(latest['Volume_Ratio'])
    macd_hist = float(latest['MACD_Hist'])
    macd = float(latest['MACD'])

    年線上方 = price > ma250 * 1.05
    是ETF = stock.replace('.TW', '').startswith('00')

    # 五項打分
    總分 = 0
    分析 = []
    顏色 = []

    # 1. 牛熊 40分
    if 年線上方:
        總分 += 40
        分析.append(f"🐮 大多頭<br>+40分<br>股價{price:.0f}>年線{ma250:.0f}")
        顏色.append("green")
    else:
        分析.append(f"🐻 空頭<br>+0分<br>股價{price:.0f}<年線{ma250*1.05:.0f}")
        顏色.append("red")

    # 2. RSI 15分
    if rsi < 30:
        總分 += 15
        分析.append(f"📊 RSI {rsi:.0f}<br>超跌區<br>+15分")
        顏色.append("green")
    elif rsi < 50:
        總分 += 10
        分析.append(f"📊 RSI {rsi:.0f}<br>中性區<br>+10分")
        顏色.append("yellow")
    elif rsi < 70:
        總分 += 5
        分析.append(f"📊 RSI {rsi:.0f}<br>偏高區<br>+5分")
        顏色.append("yellow")
    else:
        分析.append(f"📊 RSI {rsi:.0f}<br>超買區<br>+0分")
        顏色.append("red")

    # 3. 成交量 15分
    if vol_ratio > 1.5:
        總分 += 15
        分析.append(f"📈 量 {vol_ratio:.1f}倍<br>爆量<br>+15分")
        顏色.append("green")
    elif vol_ratio > 1.0:
        總分 += 10
        分析.append(f"📈 量 {vol_ratio:.1f}倍<br>正常<br>+10分")
        顏色.append("yellow")
    else:
        分析.append(f"📈 量 {vol_ratio:.1f}倍<br>萎縮<br>+0分")
        顏色.append("red")

    # 4. MACD 15分
    if macd_hist > 0 and macd > 0:
        總分 += 15
        分析.append(f"⚡ MACD {macd_hist:.2f}<br>強勢<br>+15分")
        顏色.append("green")
    elif macd_hist > 0:
        總分 += 10
        分析.append(f"⚡ MACD {macd_hist:.2f}<br>轉強<br>+10分")
        顏色.append("green")
    elif macd > 0:
        總分 += 5
        分析.append(f"⚡ MACD {macd_hist:.2f}<br>震盪<br>+5分")
        顏色.append("yellow")
    else:
        分析.append(f"⚡ MACD {macd_hist:.2f}<br>轉弱<br>+0分")
        顏色.append("red")

    # 5. 均線 15分
    if price > ma20 > ma60:
        總分 += 12
        分析.append(f"📉 均線 向上<br>+12分<br>價{price:.0f}>MA20>MA60")
        顏色.append("green")
    elif price > ma20:
        總分 += 8
        分析.append(f"📉 均線 轉強<br>+8分<br>價{price:.0f}>MA20")
        顏色.append("yellow")
    else:
        分析.append(f"📉 均線 弱勢<br>+0分<br>價{price:.0f}<MA20")
        顏色.append("red")

    # 大多頭強制100分
    if 年線上方:
        總分 = 100

    # 判斷燈號：ETF 60分，個股 70分
    門檻 = 60 if 是ETF else 70
    if 總分 >= 門檻:
        燈號 = "green"
        燈號字 = "🟢 綠燈"
        結論 = "閉眼買入" if 年線上方 else "值得買"
        值得買 = "是"
    elif 總分 >= 40:
        燈號 = "yellow"
        燈號字 = "🟡 黃燈"
        結論 = "再等等"
        值得買 = "否"
    else:
        燈號 = "red"
        燈號字 = "🔴 紅燈"
        結論 = "千萬別買"
        值得買 = "否"

    # 顯示燈號
    st.markdown("---")
    st.markdown(f"""
    <div class="light-box light-{燈號}">
        <p class="score-big">{總分}</p>
        <p class="title-big">{燈號字}</p>
        <p style="font-size: 55px; margin: 0;">{結論}</p>
        <p style="font-size: 40px; margin-top: 25px;">值不值得買：{值得買}</p>
    </div>
    """, unsafe_allow_html=True)

    # 五項分析
    st.markdown("### 💎 五項技術分析")
    cols = st.columns(5)
    for i, (文, 色) in enumerate(zip(分析, 顏色)):
        with cols[i]:
            st.markdown(f'<div class="card-box card-{色}">{文}</div>', unsafe_allow_html=True)

    # 總結
    st.markdown("### 📝 一句話總結")
    if 年線上方:
        st.success(f"大多頭：股價{price:.0f}比年線{ma250:.0f}高5%以上。趨勢向上，抱緊處理。")
    else:
        st.info(f"目前{總分}分，{'ETF要60分' if 是ETF else '個股要70分'}才綠燈。{結論}。")

    # K線圖
    st.markdown("---")
    st.markdown("### 📈 K線走勢圖")
    chart_data = pd.DataFrame({
        '股價': df['Close'],
        '20日線': df['MA20'],
        '60日線': df['MA60'],
        '年線': df['MA250']
    })
    st.line_chart(chart_data, height=500)

else:
    st.info("👆 點上方熱門標籤或輸入代號。純黑底+螢光粗邊框，字28px超粗體保證看得見。")
