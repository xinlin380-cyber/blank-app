import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt

st.set_page_config(page_title="台股五項評分", layout="wide")
st.title("台股技術分析 - 五項評分")

代號 = st.text_input("輸入股票代號", "2330")
天數 = st.slider("資料天數", 60, 365, 120)

if st.button("開始分析", type="primary"):
    if 代號.isdigit():
        代號 = 代號 + ".TW"
    
    with st.spinner("下載資料中..."):
        資料 = yf.download(代號, period=f"{天數}d")
    
    if 資料.empty:
        st.error("查無資料，請確認代號")
    else:
        收盤 = 資料['Close']
        MA5 = 收盤.rolling(5).mean().iloc[-1]
        MA20 = 收盤.rolling(20).mean().iloc[-1]
        MA60 = 收盤.rolling(60).mean().iloc[-1]
        
        # RSI計算
        delta = 收盤.diff()
        gain = delta.clip(lower=0).ewm(alpha=1/14).mean()
        loss = -delta.clip(upper=0).ewm(alpha=1/14).mean()
        rs = gain / loss
        RSI = 100 - (100 / (1 + rs))
        RSI = RSI.iloc[-1]
        
        波動 = 收盤.pct_change().std() * np.sqrt(252)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("最新收盤", f"{收盤.iloc[-1]:.2f}")
        c2.metric("RSI", f"{RSI:.1f}")
        c3.metric("年化波動", f"{波動:.1%}")
        
        分數 = 0
        if MA5 > MA20: 分數 += 1; st.success(f"1. 短期趨勢 +1 分：5日線 {MA5:.2f} > 20日線 {MA20:.2f}")
        else: st.error(f"1. 短期趨勢 +0 分：5日線 {MA5:.2f} ≤ 20日線 {MA20:.2f}")
        
        if 波動 < 0.2: 分數 += 1; st.success(f"2. 風險控制 +1 分：年化波動 {波動:.1%} < 20%")
        else: st.error(f"2. 風險控制 +0 分：年化波動 {波動:.1%} ≥ 20%")
        
        if 收盤.iloc[-1] > MA60: 分數 += 1; st.success(f"3. 長期趨勢 +1 分：收盤 > 60日線 {MA60:.2f}")
        else: st.error(f"3. 長期趨勢 +0 分：收盤 ≤ 60日線 {MA60:.2f}")
        
        量MA5 = 資料['Volume'].rolling(5).mean().iloc[-1]
        量MA20 = 資料['Volume'].rolling(20).mean().iloc[-1]
        if 量MA5 > 量MA20: 分數 += 1; st.success("4. 量能確認 +1 分：5日均量 > 20日均量")
        else: st.error("4. 量能確認 +0 分：5日均量 ≤ 20日均量")
        
        if RSI < 70: 分數 += 1; st.success(f"5. RSI安全 +1 分：RSI {RSI:.1f} < 70")
        else: st.error(f"5. RSI安全 +0 分：RSI {RSI:.1f} ≥ 70")
        
        st.subheader(f"總分：{分數} / 5 分")
        if 分數 >= 4: st.success("結論：強烈建議投資")
        elif 分數 == 3: st.info("結論：建議投資")
        elif 分數 == 2: st.warning("結論：觀望")
        else: st.error("結論：建議避開")
        
        圖, 軸 = mpf.plot(資料, type='candle', style='yahoo', volume=True, returnfig=True, figsize=(12,8))
        st.pyplot(圖)