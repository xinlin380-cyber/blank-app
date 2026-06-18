import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="台股紫光燈號", page_icon="💜", layout="wide")

# --- 紫色柔光CSS ---
st.markdown("""
<style>
   @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Noto+Sans+TC:wght@700;900&display=swap');

.stApp {
        background: #0a0a0f;
        background-image:
            radial-gradient(circle at 15% 30%, #2d1b69 0%, transparent 40%),
            radial-gradient(circle at 85% 70%, #5f0a87 0%, transparent 40%),
            radial-gradient(circle at 50% 50%, #1a1a2e 0%, #0a0a0f 100%);
    }
.main {font-family: 'Noto Sans TC', sans-serif; color: #F0F0FF;}

.stTextInput > div > div > input {
        background-color: #1a1a2e; color: #E0E0FF; border: 2px solid #8b5cf6;
        font-size: 20px; text-align: center; font-weight: bold;
        box-shadow: 0 0 10px rgba(139, 92, 246, 0.3);
    }

.neon-box {
        padding: 50px; border-radius: 30px; text-align: center; margin: 30px 0;
        border: 2px solid; position: relative; backdrop-filter: blur(10px);
    }

.neon-green {
        border-color: #a78bfa;
        background: rgba(167, 139, 250, 0.08);
        box-shadow: 0 0 15px rgba(167, 139, 250, 0.4), inset 0 0 15px rgba(167, 139, 250, 0.1);
        animation: glow-purple 3s ease-in-out infinite;
    }
.neon-yellow {
        border-color: #fbbf24;
        background: rgba(251, 191, 36, 0.08);
        box-shadow: 0 0 15px rgba(251, 191, 36, 0.4), inset 0 0 15px rgba(251, 191, 36, 0.1);
        animation: pulse-soft 2s ease-in-out infinite;
    }
.neon-red {
        border-color: #f87171;
        background: rgba(248, 113, 113, 0.08);
        box-shadow: 0 0 15px rgba(248, 113, 113, 0.4), inset 0 0 15px rgba(248, 113, 113, 0.1);
        animation: flash-soft 1.5s ease-in-out infinite;
    }

    @keyframes glow-purple {
        0%, 100% { box-shadow: 0 0 15px rgba(167, 139, 250, 0.4), inset 0 0 15px rgba(167, 139, 250, 0.1); }
        50% { box-shadow: 0 0 25px rgba(167, 139, 250, 0.6), inset 0 0 20px rgba(167, 139, 250, 0.15); }
    }
    @keyframes pulse-soft {
        0%, 100% { transform: scale(1); opacity: 0.95; }
        50% { transform: scale(1.01); opacity: 1; }
    }
    @keyframes flash-soft {
        0%, 100% { opacity: 0.95; }
        50% { opacity: 0.85; }
    }

.score-text {
        font-family: 'Orbitron', sans-serif; font-size: 90px; font-weight: 900;
        color: #FFFFFF; text-shadow: 0 0 15px rgba(255,255,255,0.5);
        margin: 0; letter-spacing: 3px;
    }
.title-text {
        font-family: 'Orbitron', sans-serif; font-size: 55px; font-weight: 900;
        color: #FFFFFF; margin: 15px 0; text-shadow: 0 0 15px rgba(255,255,255,0.5);
    }

.metric-card {
        background: rgba(26, 26, 46, 0.6); backdrop-filter: blur(10px);
        border: 2px solid #8b5cf6; padding: 20px; border-radius: 15px;
        text-align: center; box-shadow: 0 0 20px rgba(139, 92, 246, 0.2);
    }

.metric-card-red {
        background: rgba(26, 26, 46, 0.6); backdrop-filter: blur(10px);
        border: 2px solid #f87171; padding: 20px; border-radius: 15px;
        text-align: center; box-shadow: 0 0 20px rgba(248, 113, 113, 0.2);
    }

.reason-card {
        background: rgba(26, 26, 46, 0.7); backdrop-filter: blur(5px);
        border-left: 4px solid #a78bfa; padding: 20px; margin: 15px 0;
        border-radius: 12px; font-size: 18px; color: #F5F5FF;
        box-shadow: 0 4px 20px rgba(167, 139, 250, 0.15);
    }
.reason-card-red {
        background: rgba(26, 26, 46, 0.7); backdrop-filter: blur(5px);
        border-left: 4px solid #f87171; padding: 20px; margin: 15px 0;
        border-radius: 12px; font-size: 18px; color: #F5F5FF;
        box-shadow: 0 4px 20px rgba(248, 113, 113, 0.15);
    }

    h1, h2, h3, h4 {
        color: #E0E0FF!important; font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 10px rgba(224, 224, 255, 0.3);
    }
.st-emotion-cache-16txtl3,.st-emotion-cache-1y4p8pa {color: #F0F0FF!important;}
.st-emotion-cache-1xarl3l {color: #F0F0FF!important;} /* st.metric文字 */
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; font-size: 65px; color: #E0E0FF; text-shadow: 0 0 25px rgba(224, 224, 255, 0.5);'>💜 台股紫光燈號</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a78bfa; font-size: 18px;'>柔光紫調版 | 五項分析+K線+回測 | 護眼不刺眼</p>", unsafe_allow_html=True)

stock = st.text_input("", "2330", placeholder="輸入代號", label_visibility="collapsed")

if st.button("✨ 紫光掃描", use_container_width=True, type="primary"):

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
        燈號字 = "💜 紫光"
        結論 = "值得買" if not 年線上方 else "閉眼買入"
        值得買 = "是"
    elif 總分 >= 40:
        燈號 = "yellow"
        燈號字 = "💛 黃光"
        結論 = "再等等"
        值得買 = "否"
    else:
        燈號 = "red"
        燈號字 = "❤️ 紅光"
        結論 = "千萬別買"
        值得買 = "否"

    # --- 顯示紫光燈號 ---
    st.markdown("---")
    st.markdown(f"""
    <div class="neon-box neon-{燈號}">
        <p class="score-text">{總分}</p>
        <p class="title-text">{燈號字}</p>
        <p style="font-size: 36px; color: #FFFFFF; margin: 0; font-family: 'Orbitron', sans-serif;">{結論}</p>
        <p style="font-size: 24px; color: #a78bfa; margin-top: 20px;">值不值得買：{值得買}</p>
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
        '策略淨值': '💜 照燈號操作',
        '買入持有': '⚪ 無腦買入持有'
    }), height=450)

else:
    st.markdown("---")
    st.info("👆 打股票代號，按按鈕。紫光買，黃光等，紅光跑。瞎趴霓虹燈+五項分析+K線+回測一次給你。")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background: rgba(167, 139, 250, 0.15); backdrop-filter: blur(10px); padding: 30px; border-radius: 20px; text-align: center; color: white; border: 2px solid #a78bfa; box-shadow: 0 0 30px rgba(167, 139, 250, 0.4);">
            <h2 style="font-family: 'Orbitron', sans-serif; color: #a78bfa;">💜 紫光</h2>
            <p style="font-size: 24px; color: #FFFFFF;"><b>閉眼買</b></p>
            <p style="color: #E0E0FF;">大多頭or滿分</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background: rgba(251, 191, 36, 0.15); backdrop-filter: blur(10px); padding: 30px; border-radius: 20px; text-align: center; color: white; border: 2px solid #fbbf24; box-shadow: 0 0 30px rgba(251, 191, 36, 0.4);">
            <h2 style="font-family: 'Orbitron', sans-serif; color: #fbbf24;">💛 黃光</h2>
            <p style="font-size: 24px; color: #FFFFFF;"><b>再等等</b></p>
            <p style="color: #E0E0FF;">分數不夠</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background: rgba(248, 113, 113, 0.15); backdrop-filter: blur(10px); padding: 30px; border-radius: 20px; text-align: center; color: white; border: 2px solid #f87171; box-shadow: 0 0 30px rgba(248, 113, 113, 0.4);">
            <h2 style="font-family: 'Orbitron', sans-serif; color: #f87171;">❤️ 紅光</h2>
            <p style="font-size: 24px; color: #FFFFFF;"><b>別碰</b></p>
            <p style="color: #E0E0FF;">下跌趨勢</p>
        </div>
        """, unsafe_allow_html=True)
