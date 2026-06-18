import streamlit as st
import yfinance as yf
import pandas as pd
import mplfinance as mpf

st.set_page_config(page_title="台股技術分析", layout="wide")
st.title("台股技術分析 - 智能評分")

代號 = st.text_input("輸入台股代號", "2330").strip()

if st.button("開始分析", type="primary"):
    try:
        etf清單 = ['0050', '0056', '00878', '006208', '00692', '00713', '00919', '00929', '00940']
        是ETF = 代號 in etf清單

        股票代號 = f"{代號}.TW"
        # ETF抓長一點，不然MA120算不出來
        抓取期間 = "1y" if 是ETF else "6mo"
        data = yf.download(股票代號, period=抓取期間, interval="1d", progress=False, auto_adjust=True)

        if data.empty:
            st.error("抓不到資料，請確認代號正確")
            st.stop()

        開盤 = data['Open'].squeeze()
        收盤 = data['Close'].squeeze()
        最高 = data['High'].squeeze()
        最低 = data['Low'].squeeze()
        成交量 = data['Volume'].squeeze()

        plot_df = pd.DataFrame({
            'Open': 開盤, 'High': 最高, 'Low': 最低,
            'Close': 收盤, 'Volume': 成交量
        }, index=data.index)

        # 修復：min_periods=1 有多少算多少，避免NaN
        plot_df['MA5'] = 收盤.rolling(5, min_periods=1).mean()
        plot_df['MA20'] = 收盤.rolling(20, min_periods=1).mean()
        plot_df['MA60'] = 收盤.rolling(60, min_periods=1).mean()
        plot_df['MA120'] = 收盤.rolling(120, min_periods=1).mean()

        delta = 收盤.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(14, min_periods=1).mean()
        avg_loss = loss.rolling(14, min_periods=1).mean()
        rs = avg_gain / avg_loss
        plot_df['RSI'] = 100 - (100 / (1 + rs))

        收盤_乾淨 = 收盤.dropna()
        最新價 = float(收盤_乾淨.iloc[-1])
        昨收價 = float(收盤_乾淨.iloc[-2])

        # 顯示基本資訊
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("最新收盤", f"{最新價:.2f}")
        col2.metric("日漲跌幅", f"{((最新價/昨收價-1)*100):.2f}%")
        col3.metric("RSI(14)", f"{plot_df['RSI'].iloc[-1]:.1f}")
        col4.metric("成交量", f"{成交量.iloc[-1]/1000:.0f}張")

        # 畫K線圖
        st.subheader(f"K線圖 - {'ETF模式' if 是ETF else '個股模式'}")
        plot_data = plot_df.tail(120).copy()
        fig, axes = mpf.plot(plot_data, type='candle', style='yahoo',
                             mav=(5,20,60), volume=True,
                             figsize=(12,6), returnfig=True)
        st.pyplot(fig)

        # 智能評分
        st.subheader("五項技術評分")
        評分 = {}

        if 是ETF:
            # ETF用1年資料，MA120才穩
            ma120 = plot_df['MA120'].iloc[-1]
            ma60 = plot_df['MA60'].iloc[-1]
            ma120_20天前 = plot_df['MA120'].iloc[-20] if len(plot_df) >= 20 else plot_df['MA120'].iloc[0]

            ma120_斜率 = (ma120 - ma120_20天前) / ma120_20天前 * 100
            評分['長期趨勢'] = 20 if ma120_斜率 > 0 else 0

            乖離率 = (最新價 / ma120 - 1) * 100
            評分['乖離率'] = 20 if 乖離率 < -5 else 10 if 乖離率 < 0 else 0

            評分['季線'] = 20 if 最新價 > ma60 else 0

            rsi = plot_df['RSI'].iloc[-1]
            評分['動能'] = 20 if rsi < 40 else 10 if rsi < 50 else 0

            量能比 = 成交量.iloc[-1] / 成交量.rolling(20, min_periods=1).mean().iloc[-1]
            評分['籌碼安定'] = 20 if 量能比 < 1.2 and 最新價 >= 昨收價 else 10 if 量能比 < 1.5 else 0

            說明 = [
                f"MA120斜率 {ma120_斜率:.2f}%",
                f"乖離MA120 {乖離率:.2f}%",
                f"收盤 {最新價:.0f} vs MA60 {ma60:.0f}",
                f"RSI {rsi:.1f} 越低越好",
                f"量能比 {量能比:.2f}倍，縮量佳"
            ]
        else:
            ma20 = plot_df['MA20'].iloc[-1]
            ma20_5天前 = plot_df['MA20'].iloc[-5] if len(plot_df) >= 5 else plot_df['MA20'].iloc[0]

            ma20_斜率 = (ma20 - ma20_5天前) / ma20_5天前 * 100
            評分['趨勢'] = 20 if ma20_斜率 > 1 else 10 if ma20_斜率 > 0 else 0

            量能比 = 成交量.iloc[-1] / 成交量.rolling(20, min_periods=1).mean().iloc[-1]
            評分['量能'] = 20 if 量能比 > 1.5 and 最新價 > 昨收價 else 10 if 量能比 > 1 else 0

            評分['均線'] = 20 if 最新價 > ma20 else 0

            rsi = plot_df['RSI'].iloc[-1]
            評分['動能'] = 20 if 50 < rsi < 70 else 10 if 40 < rsi <= 50 else 0

            近20高 = 最高.rolling(20, min_periods=1).max().iloc[-2]
            評分['支撐壓力'] = 20 if 最新價 > 近20高 else 0

            說明 = [
                f"MA20斜率 {ma20_斜率:.2f}%",
                f"量能比 {量能比:.2f}倍",
                f"收盤 {最新價:.0f} vs MA20 {ma20:.0f}",
                f"RSI {rsi:.1f}",
                f"收盤 {最新價:.0f} vs 20日高 {近20高:.0f}"
            ]

        總分 = sum(評分.values())
        評分表 = pd.DataFrame({
            '項目': 評分.keys(), '得分': 評分.values(), '說明': 說明
        })
        st.dataframe(評分表, hide_index=True, use_container_width=True)

        if 是ETF:
            if 總分 >= 60:
                st.success(f"總分: {總分} / 100 - 適合分批存股，長期持有")
            elif 總分 >= 40:
                st.warning(f"總分: {總分} / 100 - 價格合理，可小額定期定額")
            else:
                st.error(f"總分: {總分} / 100 - 價格偏高，建議觀望或等回檔")
        else:
            if 總分 >= 60:
                st.success(f"總分: {總分} / 100 - 偏多格局，可留意買點")
            elif 總分 >= 40:
                st.warning(f"總分: {總分} / 100 - 中性盤整，觀望為主")
            else:
                st.error(f"總分: {總分} / 100 - 偏空格局，謹慎操作")

    except Exception as e:
        st.error(f"發生錯誤: {e}")
