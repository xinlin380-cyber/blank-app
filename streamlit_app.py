import streamlit as st
import yfinance as yf
import pandas as pd
import mplfinance as mpf

st.set_page_config(page_title="台股技術分析", layout="wide")
st.title("台股技術分析 - 五項評分")

代號 = st.text_input("輸入台股代號", "2330").strip()

if st.button("開始分析", type="primary"):
    try:
        股票代號 = f"{代號}.TW"
        data = yf.download(股票代號, period="6mo", interval="1d", progress=False)

        if data.empty:
            st.error("抓不到資料，請確認代號正確")
            st.stop()

        # 修復：台股會回傳DataFrame，用squeeze壓成Series
        收盤 = data['Close'].squeeze()
        最高 = data['High'].squeeze()
        最低 = data['Low'].squeeze() 
        成交量 = data['Volume'].squeeze()

        # 計算技術指標
        data['MA5'] = 收盤.rolling(5).mean()
        data['MA20'] = 收盤.rolling(20).mean()
        data['MA60'] = 收盤.rolling(60).mean()

        delta = 收盤.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        data['RSI'] = 100 - (100 / (1 + rs))

        最新價 = float(收盤.iloc[-1])
        昨收價 = float(收盤.iloc[-2])

        # 顯示基本資訊
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("最新收盤", f"{最新價:.2f}")
        col2.metric("日漲跌幅", f"{((最新價/昨收價-1)*100):.2f}%")
        col3.metric("RSI(14)", f"{data['RSI'].iloc[-1]:.1f}")
        col4.metric("成交量", f"{成交量.iloc[-1]/1000:.0f}張")

        # 畫K線圖
        st.subheader("K線圖 + MA5/MA20/MA60")
        plot_data = data.tail(120).copy()
        fig, axes = mpf.plot(plot_data, type='candle', style='yahoo',
                             mav=(5,20,60), volume=True,
                             figsize=(12,6), returnfig=True)
        st.pyplot(fig)

        # 五項評分
        st.subheader("五項技術評分")
        評分 = {}

        # 1. 趨勢：MA20斜率
        ma20_斜率 = (data['MA20'].iloc[-1] - data['MA20'].iloc[-5]) / data['MA20'].iloc[-5] * 100
        評分['趨勢'] = 20 if ma20_斜率 > 1 else 10 if ma20_斜率 > 0 else 0

        # 2. 量能：放量突破
        量能比 = 成交量.iloc[-1] / 成交量.rolling(20).mean().iloc[-1]
        評分['量能'] = 20 if 量能比 > 1.5 and 最新價 > 昨收價 else 10 if 量能比 > 1 else 0

        # 3. 均線：站上MA20
        評分['均線'] = 20 if 最新價 > data['MA20'].iloc[-1] else 0

        # 4. 動能：RSI
        rsi = data['RSI'].iloc[-1]
        評分['動能'] = 20 if 50 < rsi < 70 else 10 if 40 < rsi <= 50 else 0

        # 5. 支撐壓力：突破近20日高
        近20高 = 最高.rolling(20).max().iloc[-2]
        評分['支撐壓力'] = 20 if 最新價 > 近20高 else 0

        總分 = sum(評分.values())

        # 顯示評分表
        評分表 = pd.DataFrame({
            '項目': 評分.keys(),
            '得分': 評分.values(),
            '說明': [
                f"MA20斜率 {ma20_斜率:.2f}%",
                f"量能比 {量能比:.2f}倍",
                f"收盤 {最新價:.0f} vs MA20 {data['MA20'].iloc[-1]:.0f}",
                f"RSI {rsi:.1f}",
                f"收盤 {最新價:.0f} vs 20日高 {近20高:.0f}"
            ]
        })
        st.dataframe(評分表, hide_index=True, use_container_width=True)

        # 總分判斷
        if 總分 >= 60:
            st.success(f"總分: {總分} / 100 - 偏多格局，可留意買點")
        elif 總分 >= 40:
            st.warning(f"總分: {總分} / 100 - 中性盤整，觀望為主")
        else:
            st.error(f"總分: {總分} / 100 - 偏空格局，謹慎操作")

    except Exception as e:
        st.error(f"發生錯誤: {e}")
        st.info("可能代號錯誤或資料抓取失敗，請重試")
