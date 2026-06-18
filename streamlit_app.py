import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="台股紅綠燈", page_icon="🚦", layout="centered")

# --- 夜間護眼CSS ---
st.markdown("""
<style>
   @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@700;900&display=swap');

  .stApp {
        background-color: #0e1117;
    }
  .main {font-family: 'Noto Sans TC', sans-serif; color: #FAFAFA;}

  .stTextInput > div > div > input {
        background-color: #262730;
        color: #FAFAFA;
        border: 1px solid #464646;
    }

  .traffic-light {
        padding: 40px;
        border-radius: 25px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }

  .green-light {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        animation: glow-green 2s ease-in-out infinite;
    }

  .yellow-light {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        animation: pulse 1.5s ease-in-out infinite;
    }

  .red-light {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        animation: flash 1s ease-in-out infinite;
    }

    @keyframes glow-green {
        0%, 100% { box-shadow: 0 0 30px #38ef7d, 0 0 60px #38ef7d; }
        50% { box-shadow: 0 0 50px #38ef7d, 0 0 100px #38ef7d; }
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.03); }
    }

    @keyframes flash {
        0%, 100% { opacity: 1; box-shadow: 0 0 30px #eb3349; }
        50% { opacity: 0.8; box-shadow: 0 0 50px #eb3349; }
    }

   .score-text {
        font-size: 80px;
        font-weight: 900;
        color: white;
        text-shadow: 0 4px 15px rgba(0,0,0,0.5);
        margin: 0;
    }

   .title-text {
        font-size: 48px;
        font-weight: 900;
        color: white;
        margin: 10px 0;
    }

   .reason-box {
        background: #262730;
        border-left: 5px solid #38ef7d;
        padding: 18px;
        margin: 12px 0;
        border-radius: 12px;
        font-size: 18px;
        color: #FAFAFA;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

   .reason-box-red {
        background: #262730;
        border-left: 5px solid #eb3349;
        padding: 18px;
        margin: 12px 0;
        border-radius: 12px;
        font-size: 18px;
        color: #FAFAFA;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

   .st-emotion-cache-16txtl3 {color: #FAFAFA;} /* st.info文字 */
   .st-emotion-cache-1y4p8pa {color: #FAFAFA;} /* st.success文字 */
    h1, h2, h3 {color: #FAFAFA!important;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; font-size: 50px; color: #FAFAFA;'>🚦 台股紅綠燈</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; font-size: 18px;'>夜間護眼版 | 看燈號就知道能不能買</p>", unsafe_allow_html=True)

stock = st.text_input("", "2330", placeholder="輸入股票代號，例如 2330、0050、00878", label_visibility="collapsed")

if st.button("🔍 查燈號", use_container_width=True, type="primary"):

    with st.spinner("🚀 正在讀取市場情緒..."):
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

    # --- 計算 ---
    ma250 = df['Close'].rolling(250).mean().iloc[-1]
    price = df['Close'].iloc[-1]
    年線上方 = price > ma250 * 1.05

    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
    loss = -delta.where(delta < 0, 0).rolling(14).mean().iloc[-1]
    rs = gain / loss if loss!= 0 else 100
    rsi = 100 - (100 / (1 + rs))

    vol_ma = df['Volume'].rolling(20).mean().iloc[-1]
    vol_ratio = df['Volume'].iloc[-1] / vol_ma

    ma20 = df['Close'].rolling(20).mean().iloc[-1]
    ma60 = df['Close'].rolling(60).mean().iloc[-1]
    趨勢向上 = price > ma20 > ma60
    是ETF = stock.replace('.TW', '').startswith('00')

    # --- 打分 ---
    分數 = 0
    原因 = []
    原因類型 = [] # 用來判斷綠色還是紅色邊框

    if 年線上方:
        分數 = 100
        燈號 = "green"
        燈號字 = "🟢 綠燈"
        結論 = "閉眼買入"
        原因.append(f"✅ 現在 {price:.0f} 元，比過去1年平均 {ma250:.0f} 元貴很多")
        原因類型.append("green")
        原因.append("✅ 所有人都在賺錢，大多頭市場不會輕易結束")
        原因類型.append("green")
        原因.append("⛔ 你現在賣掉，過3個月會搥心肝")
        原因類型.append("red")
    else:
        if rsi < 30:
            分數 += 25
            原因.append(f"✅ RSI {rsi:.0f} 大家恐慌亂砍，撿便宜好時機")
            原因類型.append("green")
        elif rsi < 50:
            分數 += 15
            原因.append(f"⚠️ RSI {rsi:.0f} 價格普通，不貴不便宜")
            原因類型.append("yellow")
        else:
            原因.append(f"❌ RSI {rsi:.0f} 太貴了，大家在FOMO亂追高")
            原因類型.append("red")

        if vol_ratio > 1.5:
            分數 += 25
            原因.append(f"✅ 成交量爆 {vol_ratio:.1f} 倍，有大戶在偷偷買")
            原因類型.append("green")
        elif vol_ratio > 1.0:
            分數 += 15
            原因.append(f"⚠️ 成交量 {vol_ratio:.1f} 倍，還算正常")
            原因類型.append("yellow")
        else:
            原因.append(f"❌ 成交量剩 {vol_ratio:.1f} 倍，沒人要，死水一潭")
            原因類型.append("red")

        if 趨勢向上:
            分數 += 50
            原因.append(f"✅ 短線漲過長線，代表趨勢往上，順風車")
            原因類型.append("green")
        else:
            原因.append(f"❌ 短線跌破長線，代表趨勢往下，逆風不要上")
            原因類型.append("red")

        門檻 = 60 if 是ETF else 70
        if 分數 >= 門檻:
            燈號 = "green"
            燈號字 = "🟢 綠燈"
            結論 = "可以買了"
        elif 分數 >= 40:
            燈號 = "yellow"
            燈號字 = "🟡 黃燈"
            結論 = "再等等"
        else:
            燈號 = "red"
            燈號字 = "🔴 紅燈"
            結論 = "千萬別買"

    # --- 顯示酷炫燈號 ---
    st.markdown("---")

    st.markdown(f"""
    <div class="traffic-light {燈號}-light">
        <p class="score-text">{分數}分</p>
        <p class="title-text">{燈號字}</p>
        <p style="font-size: 32px; color: white; margin: 0;">{結論}</p>
    </div>
    """, unsafe_allow_html=True)

    # 為什麼
    st.markdown("### 📝 AI幫你看盤結論")
    for i, r in enumerate(原因):
        box_class = "reason-box" if 原因類型[i] == "green" else "reason-box-red"
        st.markdown(f'<div class="{box_class}">{i+1}. {r}</div>', unsafe_allow_html=True)

    # 白話總結
    st.markdown("---")
    if 年線上方:
        st.success("💡 **一句話總結**：這支股票所有投資人平均都賺錢，市場氣氛超嗨。現在賣=幫別人抬轎，抱緊持有一年再來看。")
    else:
        if 是ETF:
            st.info(f"💡 **一句話總結**：ETF要 {門檻} 分才能買，現在 {分數} 分{結論}。ETF要等大盤崩一起撿，現在買會套在高點。")
        else:
            st.info(f"💡 **一句話總結**：個股要 {門檻} 分才能買，現在 {分數} 分{結論}。趨勢往下時進場，下場就是幫人接刀子。")

else:
    st.markdown("---")
    st.info("👆 打股票代號，按按鈕。綠燈買，黃燈等，紅燈跑。")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 20px; border-radius: 15px; text-align: center; color: white;">
            <h2>🟢 綠燈</h2>
            <p><b>閉眼買</b></p>
            <p>大多頭or分數達標</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%); padding: 20px; border-radius: 15px; text-align: center; color: white;">
            <h2>🟡 黃燈</h2>
            <p><b>再等等</b></p>
            <p>分數不夠，等跌</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); padding: 20px; border-radius: 15px; text-align: center; color: white;">
            <h2>🔴 紅燈</h2>
            <p><b>別碰</b></p>
            <p>下跌趨勢，買就套</p>
        </div>
        """, unsafe_allow_html=True)
      
