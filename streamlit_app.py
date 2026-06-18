import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="台股霓虹燈號", page_icon="💎", layout="wide")

# --- 瞎趴霓虹CSS ---
st.markdown("""
<style>
   @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Noto+Sans+TC:wght@700;900&display=swap');

.stApp {
        background: #000000;
        background-image:
            radial-gradient(circle at 20% 50%, #120078 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, #9d0191 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, #fd3a69 0%, transparent 50%);
    }
.main {font-family: 'Noto Sans TC', sans-serif; color: #FFFFFF;}

.stTextInput > div > div > input {
        background-color: #1a1a2e; color: #00ff88; border: 2px solid #00ff88;
        font-size: 20px; text-align: center; font-weight: bold;
    }

.neon-box {
        padding: 50px; border-radius: 30px; text-align: center; margin: 30px 0;
        border: 3px solid; position: relative;
    }

.neon-green {
        border-color: #00ff88;
        background: rgba(0, 255, 136, 0.1);
        box-shadow: 0 0 20px #00ff88, 0 0 40px #00ff88, inset 0 0 20px rgba(0, 255, 136, 0.2);
        animation: flicker-green 3s infinite;
    }
.neon-yellow {
        border-color: #ffff00;
        background: rgba(255, 255, 0, 0.1);
        box-shadow: 0 0 20px #ffff00, 0 0 40px #ffff00, inset 0 0 20px rgba(255, 255, 0, 0.2);
        animation: pulse-yellow 2s infinite;
    }
.neon-red {
        border-color: #ff0040;
        background: rgba(255, 0, 64, 0.1);
        box-shadow: 0 0 20px #ff0040, 0 0 40px #ff0040, inset 0 0 20px rgba(255, 0, 64, 0.2);
        animation: flash-red 1s infinite;
    }

    @keyframes flicker-green {
        0%, 100% { opacity: 1; box-shadow: 0 0 20px #00ff88, 0 0 40px #00ff88; }
        50% { opacity: 0.9; box-shadow: 0 0 30px #00ff88, 0 0 60px #00ff88; }
    }
    @keyframes pulse-yellow {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    @keyframes flash-red {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }

.score-text {
        font-family: 'Orbitron', sans-serif; font-size: 100px; font-weight: 900;
        color: #FFFFFF; text-shadow: 0 0 20px currentColor, 0 0 40px currentColor;
        margin: 0; letter-spacing: 5px;
    }
.title-text {
        font-family: 'Orbitron', sans-serif; font-size: 60px; font-weight: 900;
        color: #FFFFFF; margin: 20px 0; text-shadow: 0 0 20px currentColor;
    }

.metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid #00ff88; padding: 20px; border-radius: 15px;
        text-align: center; box-shadow: 0 0 15px rgba(0, 255, 136, 0.3);
    }

.metric-card-red {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid #ff0040; padding: 20px; border-radius: 15px;
        text-align: center; box-shadow: 0 0 15px rgba(255, 0, 64, 0.3);
    }

.reason-card {
        background: #1a1a2e; border-left: 4px solid #00ff88; padding: 20px; margin: 15px 0;
        border-radius: 10px; font-size: 18px; color: #FFFFFF;
        box-shadow: 0 4px 15px rgba(0, 255, 136, 0.2);
    }
.reason-card-red {
        background: #1a1a2e; border-left: 4px solid #ff0040; padding: 20px; margin: 15px 0;
        border-radius: 10px; font-size: 18px; color: #FFFFFF;
        box-shadow: 0 4px 15px rgba(255, 0, 64, 0.2);
    }

    h1, h2, h3, h4 {color: #00ff88!important; font-family: 'Orbitron', sans-serif; text-shadow: 0 0 10px #00ff88;}
  .st-emotion-cache-16txtl3,.st-emotion-cache-1y4p8pa {color: #FFFFFF;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; font-size: 70px; color: #00ff88; text-shadow: 0 0 30px #00ff88;'>💎 台股霓虹燈號</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; font-size: 20px;'>黑底霓虹版 | 五項分析+K線+回測 | 瞎趴到爆</p>", unsafe_allow_html=True)

stock = st.text_input("", "2330", placeholder="輸入代號", label_visibility="collapsed")

if st.button("🔥 開始掃描", use_container_width=True, type="primary"):

    with st.spinner("⚡ 霓虹燈號掃描中..."):
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

    # --- 計算五項指標 ---
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

    # --- 取最新值 ---
    latest = df.iloc[-1]
    price = latest['Close']
    ma250 = latest['MA250']
    ma20 = latest['MA20']
    ma60 = latest['MA60']
    rsi = latest['RSI']
    vol_ratio = latest['Volume_Ratio']
    macd_hist = latest['MACD_Hist']
    macd = latest['MACD']
    bb_upper = latest['BB_Upper']
    bb_lower = latest['BB_Lower']

    年線上方 = price > ma250 * 1.05
    趨勢向上 = price > ma20 > ma60
    是ETF = stock.replace('.TW', '').startswith('00')

    # --- 五項打分 ---
    總分 = 0
    五項分析 = []
    五項顏色 = []

    # 1. 牛熊判斷 - 佔40分
    if 年線上方:
        牛熊分 = 40
        五項分析.append(f"🐮 牛熊狀態：大多頭｜+{牛熊分}分｜股價{price:.0f} > 年線{ma250:.0f}*1.05")
        五項顏色.append("green")
        總分 += 牛熊分
    else:
        牛熊分 = 0
        五項分析.append(f"🐻 牛熊狀態：震盪/空頭｜+{牛熊分}分｜股價{price:.0f} < 年線{ma250*1.05:.0f}")
        五項顏色.append("red")

    # 2. RSI超買超賣 - 佔15分
    if rsi < 30:
        rsi分 = 15
        五項分析.append(f"📊 RSI指標：{rsi:.0f} 超跌區｜+{rsi分}分｜大家恐慌亂砍")
        五項顏色.append("green")
    elif rsi < 50:
        rsi分 = 10
        五項分析.append(f"📊 RSI指標：{rsi:.0f} 中性區｜+{rsi分}分｜價格普通")
        五項顏色.append("yellow")
    elif rsi < 70:
        rsi分 = 5
        五項分析.append(f"📊 RSI指標：{rsi:.0f} 偏高區｜+{rsi分}分｜小心追高")
        五項顏色.append("yellow")
    else:
        rsi分 = 0
        五項分析.append(f"📊 RSI指標：{rsi:.0f} 超買區｜+{rsi分}分｜FOMO追高危險")
        五項顏色.append("red")
    總分 += rsi分

    # 3. 成交量 - 佔15分
    if vol_ratio > 1.5:
        量分 = 15
        五項分析.append(f"📈 成交量：{vol_ratio:.1f}倍爆量｜+{量分}分｜大戶進場")
        五項顏色.append("green")
    elif vol_ratio > 1.0:
        量分 = 10
        五項分析.append(f"📈 成交量：{vol_ratio:.1f}倍正常｜+{量分}分")
        五項顏色.append("yellow")
    else:
        量分 = 0
        五項分析.append(f"📈 成交量：{vol_ratio:.1f}倍萎縮｜+{量分}分｜沒人要")
        五項顏色.append("red")
    總分 += 量分

    # 4. MACD - 佔15分
    if macd_hist > 0 and macd > 0:
        macd分 = 15
        五項分析.append(f"⚡ MACD動能：{macd_hist:.2f} 強勢｜+{macd分}分｜多頭動能強")
        五項顏色.append("green")
    elif macd_hist > 0:
        macd分 = 10
        五項分析.append(f"⚡ MACD動能：{macd_hist:.2f} 轉強｜+{macd分}分")
        五項顏色.append("green")
    elif macd > 0:
        macd分 = 5
        五項分析.append(f"⚡ MACD動能：{macd_hist:.2f} 震盪｜+{macd分}分")
        五項顏色.append("yellow")
    else:
        macd分 = 0
        五項分析.append(f"⚡ MACD動能：{macd_hist:.2f} 轉弱｜+{macd分}分｜空頭動能")
        五項顏色.append("red")
    總分 += macd分

    # 5. 均線布林 - 佔15分
    if price > ma20 > ma60 and price > bb_upper:
        均線分 = 15
        五項分析.append(f"📉 均線布林：價{price:.0f}>MA20{ma20:.0f}>MA60{ma60:.0f}｜+{均線分}分｜強勢突破")
        五項顏色.append("green")
    elif price > ma20 > ma60:
        均線分 = 12
        五項分析.append(f"📉 均線布林：價{price:.0f}>MA20{ma20:.0f}>MA60{ma60:.0f}｜+{均線分}分｜趨勢向上")
        五項顏色.append("green")
    elif price > ma20:
        均線分 = 8
        五項分析.append(f"📉 均線布林：價{price:.0f}>MA20{ma20:.0f}｜+{均線分}分｜短期轉強")
        五項顏色.append("yellow")
    elif price > bb_lower:
        均線分 = 4
        五項分析.append(f"📉 均線布林：價{price:.0f}在布林內｜+{均線分}分｜震盪")
        五項顏色.append("yellow")
    else:
        均線分 = 0
        五項分析.append(f"📉 均線布林：價{price:.0f}跌破支撐｜+{均線分}分｜弱勢")
        五項顏色.append("red")
    總分 += 均線分

    # --- 大多頭強制100分 ---
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

    # --- 顯示霓虹燈號 ---
    st.markdown("---")
    st.markdown(f"""
    <div class="neon-box neon-{燈號}">
        <p class="score-text">{總分}</p>
        <p class="title-text">{燈號字}</p>
        <p style="font-size: 36px; color: white; margin: 0; font-family: 'Orbitron', sans-serif;">{結論}</p>
        <p style="font-size: 24px; color: #00ff88; margin-top: 20px;">值不值得買：{值得買}</p>
    </div>
    """, unsafe_allow_html=True)

    # --- 五項分析卡片 ---
    st.markdown("### 💎 五項技術分析")
    cols = st.columns(5)
    for i, (分析, 顏色) in enumerate(zip(五項分析, 五項顏色)):
        with cols[i]:
            card_class = "metric-card" if 顏色 == "green" else "metric-card-red"
            st.markdown(f'<div class="{card_class}">{分析}</div>', unsafe_allow_html=True)

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

    # --- 2年歷史回測 ---
    st.markdown("---")
    st.markdown("### 📊 2年歷史回測：照燈號操作vs買入持有")

    # 簡易回測邏輯
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

        if score == 100: # 大多頭滿倉
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
        '策略淨值': '🔵 照燈號操作',
        '買入持有': '⚪ 無腦買入持有'
    }), height=450)

else:
    st.markdown("---")
    st.info("👆 打股票代號，按按鈕。瞎趴霓虹燈+五項分析+K線+回測一次給你。")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 30px; border-radius: 20px; text-align: center; color: white; box-shadow: 0 0 30px #00ff88;">
            <h2 style="font-family: 'Orbitron', sans-serif;">🟢 綠燈</h2>
            <p style="font-size: 24px;"><b>閉眼買</b></p>
            <p>大多頭or滿分</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%); padding: 30px; border-radius: 20px; text-align: center; color: white; box-shadow: 0 0 30px #ffff00;">
            <h2 style="font-family: 'Orbitron', sans-serif;">🟡 黃燈</h2>
            <p style="font-size: 24px;"><b>再等等</b></p>
            <p>分數不夠</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); padding: 30px; border-radius: 20px; text-align: center; color: white; box-shadow: 0 0 30px #ff0040;">
            <h2 style="font-family: 'Orbitron', sans-serif;">🔴 紅燈</h2>
            <p style="font-size: 24px;"><b>別碰</b></p>
            <p>下跌趨勢</p>
        </div>
        """, unsafe_allow_html=True)
