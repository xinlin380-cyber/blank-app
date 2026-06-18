import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="台股紫光燈號", page_icon="💜", layout="wide")

# --- L10.7 修復版CSS：字強制亮白+黃燈補上 ---
st.markdown("""
<style>
   @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Noto+Sans+TC:wght@700;900&display=swap');

.stApp {
        background: #0F0F1A;
        background-image:
            radial-gradient(circle at 15% 30%, #2A1F3D 0%, transparent 45%),
            radial-gradient(circle at 85% 70%, #3D1F4A 0%, transparent 45%),
            radial-gradient(circle at 50% 50%, #15151F 0%, #0F0F1A 100%);
    }
.main {font-family: 'Noto Sans TC', sans-serif;}

/* 強制所有字白色發光 */
* {
    color: #FFFFFF!important;
    text-shadow: 0 0 8px rgba(255,255,255,0.35)!important;
}

.stTextInput > div > div > input {
        background-color: #1A1A2A!important;
        color: #FFFFFF!important;
        border: 2px solid #D4E8D4!important;
        font-size: 20px; text-align: center; font-weight: bold;
        box-shadow: 0 0 12px rgba(212, 232, 212, 0.25)!important;
    }
.stTextInput > div > div > input::placeholder {color: #A0A0B8!important;}

.neon-box {
        padding: 50px; border-radius: 30px; text-align: center; margin: 30px 0;
        border: 2px solid; position: relative; backdrop-filter: blur(12px);
    }

.neon-green {
        border-color: #D4E8D4;
        background: rgba(26, 26, 42, 0.9);
        box-shadow: 0 0 25px rgba(212, 232, 212, 0.4), inset 0 0 25px rgba(212, 232, 212, 0.1);
    }
.neon-yellow {
        border-color: #E8D4A1;
        background: rgba(26, 26, 42, 0.9);
        box-shadow: 0 0 25px rgba(232, 212, 161, 0.4), inset 0 0 25px rgba(232, 212, 161, 0.1);
    }
.neon-red {
        border-color: #E8A1A1;
        background: rgba(26, 26, 42, 0.9);
        box-shadow: 0 0 25px rgba(232, 161, 161, 0.4), inset 0 0 25px rgba(232, 161, 161, 0.1);
    }

.score-text {
        font-family: 'Orbitron', sans-serif; font-size: 90px; font-weight: 900;
        color: #FFFFFF!important; text-shadow: 0 0 15px rgba(255,255,255,0.5)!important;
        margin: 0; letter-spacing: 3px;
    }
.title-text {
        font-family: 'Orbitron', sans-serif; font-size: 55px; font-weight: 900;
        color: #FFFFFF!important; margin: 15px 0;
        text-shadow: 0 0 15px rgba(255,255,255,0.5)!important;
    }

/* 卡片三色全補上 */
.metric-card-green {
        background: #1A1A2A!important; backdrop-filter: blur(10px);
        border: 2px solid #D4E8D4!important; padding: 20px; border-radius: 15px;
        text-align: center; box-shadow: 0 0 20px rgba(212, 232, 212, 0.3)!important;
        color: #FFFFFF!important;
    }
.metric-card-yellow {
        background: #1A1A2A!important; backdrop-filter: blur(10px);
        border: 2px solid #E8D4A1!important; padding: 20px; border-radius: 15px;
        text-align: center; box-shadow: 0 0 20px rgba(232, 212, 161, 0.3)!important;
        color: #FFFFFF!important;
    }
.metric-card-red {
        background: #1A1A2A!important; backdrop-filter: blur(10px);
        border: 2px solid #E8A1A1!important; padding: 20px; border-radius: 15px;
        text-align: center; box-shadow: 0 0 20px rgba(232, 161, 161, 0.3)!important;
        color: #FFFFFF!important;
    }

/* 強制卡片內文字 */
.metric-card-green *,.metric-card-yellow *,.metric-card-red * {
        color: #FFFFFF!important;
        text-shadow: 0 0 8px rgba(255,255,255,0.4)!important;
        font-weight: bold!important;
    }

.reason-card {
        background: #1A1A2A!important; backdrop-filter: blur(8px);
        border-left: 6px solid #D4E8D4; padding: 20px; margin: 15px 0;
        border-radius: 12px; font-size: 18px; color: #FFFFFF!important;
        text-shadow: 0 0 8px rgba(255,255,255,0.35)!important;
        box-shadow: 0 4px 25px rgba(212, 232, 212, 0.2)!important;
    }

    h1, h2, h3, h4, p, div, span {
        color: #FFFFFF!important;
        text-shadow: 0 0 8px rgba(255, 255, 255, 0.35)!important;
    }

/* Streamlit警告/成功訊息也改白色 */
.stAlert {
        background-color: #1A1A2A!important;
        color: #FFFFFF!important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; font-size: 65px;'>💜 台股紫光燈號</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #D4E8D4; font-size: 18px;'>莫蘭迪高對比修復版 | 字強制亮白</p>", unsafe_allow_html=True)

# --- 熱門清單 ---
st.markdown("<p style='text-align: center; color: #A0A0B8; font-size: 16px; margin-top: 20px;'>🔥 熱門追蹤</p>", unsafe_allow_html=True)

hot_stocks = {
    "台積電2330": "2330",
    "0050": "0050",
    "00878": "00878",
    "長榮2603": "2603",
    "鴻海2317": "2317"
}

cols = st.columns(5)
for i, (name, code) in enumerate(hot_stocks.items()):
    with cols[i]:
        if st.button(name, key=f"hot_{code}", use_container_width=True):
            st.session_state.stock_input = code

if 'stock_input' not in st.session_state:
    st.session_state.stock_input = ""

stock = st.text_input("", value=st.session_state.stock_input, placeholder="輸入代號或點上方熱門", label_visibility="collapsed", key="input_box")

if st.button("✨ 紫光掃描", use_container_width=True, type="primary") or stock:

    if not stock:
        st.warning("👆 請輸入代號或點選熱門標籤")
        st.stop()

    with st.spinner("🌌 紫光能量掃描中..."):
        try:
            ticker = f"{stock}.TW" if not stock.endswith('.TW') else stock
            df = yf.download(ticker, period="2y", progress=False)
            if df.empty:
                st.error("❌ 查無此股票")
                st.stop()
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.dropna()
        except:
            st.error("❌ 網路錯誤")
            st.stop()

    # --- 計算指標 ---
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

    std = df['Close'].rolling(20).std()
    df['BB_Upper'] = df['MA20'] + 2 * std
    df['BB_Lower'] = df['MA20'] - 2 * std

    df = df.dropna()

    latest = df.iloc[-1]
    price = latest['Close']
    ma250 = latest['MA250']
    ma20 = latest['MA20']
    ma60 = latest['MA60']
    rsi = latest['RSI']
    vol_ratio = latest['Volume_Ratio']
    macd_hist = latest['MACD_Hist']
    macd = latest['MACD']

    年線上方 = price > ma250 * 1.05
    是ETF = stock.replace('.TW', '').startswith('00')

    # --- 五項打分 + 顏色判斷 ---
    總分 = 0
    五項分析 = []
    五項顏色 = []

    # 1. 牛熊
    if 年線上方:
        總分 += 40
        五項分析.append(f"🐮 牛熊狀態：大多頭｜+40分<br>股價{price:.0f} > 年線{ma250:.0f}*1.05")
        五項顏色.append("green")
    else:
        五項分析.append(f"🐻 牛熊狀態：震盪/空頭｜+0分<br>股價{price:.0f} < 年線{ma250*1.05:.0f}")
        五項顏色.append("red")

    # 2. RSI
    if rsi < 30:
        總分 += 15
        五項分析.append(f"📊 RSI指標：{rsi:.0f} 超跌區｜+15分<br>大家恐慌亂砍")
        五項顏色.append("green")
    elif rsi < 50:
        總分 += 10
        五項分析.append(f"📊 RSI指標：{rsi:.0f} 中性區｜+10分<br>價格普通")
        五項顏色.append("yellow")
    elif rsi < 70:
        總分 += 5
        五項分析.append(f"📊 RSI指標：{rsi:.0f} 偏高區｜+5分<br>小心追高")
        五項顏色.append("yellow")
    else:
        五項分析.append(f"📊 RSI指標：{rsi:.0f} 超買區｜+0分<br>FOMO追高危險")
        五項顏色.append("red")

    # 3. 成交量
    if vol_ratio > 1.5:
        總分 += 15
        五項分析.append(f"📈 成交量：{vol_ratio:.1f}倍爆量｜+15分<br>大戶進場")
        五項顏色.append("green")
    elif vol_ratio > 1.0:
        總分 += 10
        五項分析.append(f"📈 成交量：{vol_ratio:.1f}倍正常｜+10分")
        五項顏色.append("yellow")
    else:
        五項分析.append(f"📈 成交量：{vol_ratio:.1f}倍萎縮｜+0分<br>沒人要")
        五項顏色.append("red")

    # 4. MACD
    if macd_hist > 0 and macd > 0:
        總分 += 15
        五項分析.append(f"⚡ MACD動能：{macd_hist:.2f} 強勢｜+15分<br>多頭動能強")
        五項顏色.append("green")
    elif macd_hist > 0:
        總分 += 10
        五項分析.append(f"⚡ MACD動能：{macd_hist:.2f} 轉強｜+10分")
        五項顏色.append("green")
    elif macd > 0:
        總分 += 5
        五項分析.append(f"⚡ MACD動能：{macd_hist:.2f} 震盪｜+5分")
        五項顏色.append("yellow")
    else:
        五項分析.append(f"⚡ MACD動能：{macd_hist:.2f} 轉弱｜+0分<br>空頭動能")
        五項顏色.append("red")

    # 5. 均線
    if price > ma20 > ma60 and price > df['BB_Upper'].iloc[-1]:
        總分 += 15
        五項分析.append(f"📉 均線布林：強勢突破｜+15分<br>價{price:.0f}>MA20{ma20:.0f}>MA60{ma60:.0f}")
        五項顏色.append("green")
    elif price > ma20 > ma60:
        總分 += 12
        五項分析.append(f"📉 均線布林：趨勢向上｜+12分<br>價{price:.0f}>MA20{ma20:.0f}>MA60{ma60:.0f}")
        五項顏色.append("green")
    elif price > ma20:
        總分 += 8
        五項分析.append(f"📉 均線布林：短期轉強｜+8分<br>價{price:.0f}>MA20{ma20:.0f}")
        五項顏色.append("yellow")
    elif price > df['BB_Lower'].iloc[-1]:
        總分 += 4
        五項分析.append(f"📉 均線布林：在布林內｜+4分<br>震盪")
        五項顏色.append("yellow")
    else:
        五項分析.append(f"📉 均線布林：跌破支撐｜+0分<br>弱勢")
        五項顏色.append("red")

    if 年線上方:
        總分 = 100

    # --- 判斷燈號 ---
    門檻 = 60 if 是ETF else 70
    if 總分 >= 門檻:
        燈號 = "green"
        燈號字 = "🟢 綠燈"
        結論 = "值得買" if not 年線上方 else "閉眼買入"
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

    # --- 顯示燈號 ---
    st.markdown("---")
    st.markdown(f"""
    <div class="neon-box neon-{燈號}">
        <p class="score-text">{總分}</p>
        <p class="title-text">{燈號字}</p>
        <p style="font-size: 36px; color: #FFFFFF; margin: 0; font-family: 'Orbitron', sans-serif;">{結論}</p>
        <p style="font-size: 24px; color: #D4E8D4; margin-top: 20px;">值不值得買：{值得買}</p>
    </div>
    """, unsafe_allow_html=True)

    # --- 五項分析卡片 ---
    st.markdown("### 💎 五項技術分析")
    cols = st.columns(5)
    for i, (分析, 顏色) in enumerate(zip(五項分析, 五項顏色)):
        with cols[i]:
            st.markdown(f'<div class="metric-card-{顏色}">{分析}</div>', unsafe_allow_html=True)

    # --- 白話結論 ---
    st.markdown("### 📝 為什麼這樣打分")
    if 年線上方:
        st.success("💡 **一句話總結**：股價比年線高5%以上 = 大多頭。所有人都賺錢，市場FOMO情緒重。現在賣=幫別人抬轎，抱一年再看。")
    else:
        if 是ETF:
            st.info(f"💡 **一句話總結**：ETF要{門檻}分才值得買，現在{總分}分{結論}。ETF要等大盤崩一起撿便宜，現在買會套高點。")
        else:
            st.info(f"💡 **一句話總結**：個股要{門檻}分才值得買，現在{總分}分{結論}。趨勢往下時進場=幫人接刀子，等站上MA20再說。")

    # --- K線圖 ---
    st.markdown("---")
    st.markdown("### 📈 K線走勢圖")
    chart_data = pd.DataFrame({
        '股價': df['Close'],
        '20日線': df['MA20'],
        '60日線': df['MA60'],
        '年線': df['MA250']
    })
    st.line_chart(chart_data, height=450)

    # --- 回測 ---
    st.markdown("---")
    st.markdown("### 📊 2年歷史回測：照燈號操作vs買入持有")

    scores_hist = []
    for i in range(len(df)):
        if i < 250:
            scores_hist.append(50)
        else:
            temp_price = df['Close'].iloc[i]
            temp_ma250 = df['MA250'].iloc[i]
            temp_bull = temp_price > temp_ma250 * 1.05
            scores_hist.append(100 if temp_bull else 50)

    df['Score'] = scores_hist
    position = 0
    equity = [1.0]

    for i in range(1, len(df)):
        price_now = df['Close'].iloc[i]
        prev_price = df['Close'].iloc[i-1]
        score = df['Score'].iloc[i]

        if score == 100:
            position = 1
        else:
            if position == 0 and score >= 門檻:
                position = 1
            elif position == 1 and score < 40:
                position = 0

        ret = price_now / prev_price if position == 1 else 1.0
        equity.append(equity[-1] * ret)

    df['策略淨值'] = equity
    df['買入持有'] = df['Close'] / df['Close'].iloc[0]

    策略報酬 = (equity[-1] - 1) * 100
    大盤報酬 = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
    超額報酬 = 策略報酬 - 大盤報酬

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 策略報酬", f"{策略報酬:.1f}%", f"{超額報酬:.1f}% vs大盤")
    col2.metric("📈 大盤報酬", f"{大盤報酬:.1f}%")
    col3.metric("🎯 模式", "ETF寬鬆" if 是ETF else "個股嚴格")
    col4.metric("⚡ 值不值得買", 值得買)

    st.line_chart(df[['策略淨值', '買入持有']].rename(columns={
        '策略淨值': '💜 照燈號操作',
        '買入持有': '⚪ 無腦買入持有'
    }), height=450)

else:
    st.markdown("---")
    st.info("👆 打股票代號或點上方熱門標籤。莫蘭迪配色+高對比，優雅且清楚。")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background: rgba(26, 26, 42, 0.9); backdrop-filter: blur(12px); padding: 30px; border-radius: 20px; text-align: center; color: white; border: 2px solid #D4E8D4; box-shadow: 0 0 30px rgba(212, 232, 212, 0.4);">
            <h2 style="font-family: 'Orbitron', sans-serif; color: #D4E8D4;">🟢 綠燈</h2>
            <p style="font-size: 24px; color: #FFFFFF;"><b>閉眼買</b></p>
            <p style="color: #E0E0FF;">大多頭or滿分</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background: rgba(26, 26, 42, 0.9); backdrop-filter: blur(12px); padding: 30px; border-radius: 20px; text-align: center; color: white; border: 2px solid #E8D4A1; box-shadow: 0 0 30px rgba(232, 212, 161, 0.4);">
            <h2 style="font-family: 'Orbitron', sans-serif; color: #E8D4A1;">🟡 黃燈</h2>
            <p style="font-size: 24px; color: #FFFFFF;"><b>再等等</b></p>
            <p style="color: #E0E0FF;">分數不夠</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background: rgba(26, 26, 42, 0.9); backdrop-filter: blur(12px); padding: 30px; border-radius: 20px; text-align: center; color: white; border: 2px solid #E8A1A1; box-shadow: 0 0 30px rgba(232, 161, 161, 0.4);">
            <h2 style="font-family: 'Orbitron', sans-serif; color: #E8A1A1;">🔴 紅燈</h2>
            <p style="font-size: 24px; color: #FFFFFF;"><b>別碰</b></p>
            <p style="color: #E0E0FF;">下跌趨勢</p>
        </div>
        """, unsafe_allow_html=True)
