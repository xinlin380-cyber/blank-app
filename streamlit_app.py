import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="台股智能診斷 Pro", page_icon="📈", layout="wide")
st.title("📈 台股智能診斷 Pro")
st.caption("L7.3 Debug版 | 強制顯示年線數值")

stock = st.text_input("輸入台股代號", "2330", help="個股：2330｜ETF：0050、006208、00878")
col1, col2 = st.columns([1, 1])
with col1:
    diagnose_btn = st.button("🚀 開始診斷", use_container_width=True)
with col2:
    backtest_btn = st.button("📊 回測2年", use_container_width=True)

def get_stock_data(ticker, period="3y"): # 改3年確保有250日
    try:
        if not ticker.endswith('.TW'):
            ticker = f"{ticker}.TW"
        df = yf.download(ticker, period=period, progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df.dropna()
    except: return None

def calculate_indicators(df):
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

    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA60'] = df['Close'].rolling(60).mean()
    df['MA250'] = df['Close'].rolling(250).mean()
    std = df['Close'].rolling(20).std()
    df['BB_Upper'] = df['MA20'] + 2 * std
    df['BB_Lower'] = df['MA20'] - 2 * std

    return df.dropna()

def is_etf(ticker):
    return ticker.replace('.TW', '').startswith('00')

def detect_bull_market(df):
    if len(df) < 250: return False, 0, 0
    ma250 = df['MA250'].iloc[-1]
    price = df['Close'].iloc[-1]
    is_bull = price > ma250 * 1.05
    return is_bull, price, ma250 # 回傳3個值用來debug

def get_score(df, ticker):
    latest = df.iloc[-1]
    score = 0
    details = {}
    bull_market, price, ma250 = detect_bull_market(df)
    etf_mode = is_etf(ticker)

    # Debug資訊直接塞進details
    details['【Debug】股價'] = f"{price:.0f}"
    details['【Debug】年線MA250'] = f"{ma250:.0f}"
    details['【Debug】年線*1.05'] = f"{ma250*1.05:.0f}"
    details['【Debug】是否大多頭'] = f"{bull_market}"

    if bull_market:
        details['牛熊判斷'] = f"股價{price:.0f} > 年線{ma250:.0f}*1.05 | 大多頭"
        return 100, details, bull_market, etf_mode

    rsi = latest['RSI']
    if rsi < 30: rsi_score = 20
    elif rsi < 50: rsi_score = 15
    elif rsi < 70: rsi_score = 10
    else: rsi_score = 0
    score += rsi_score
    details['RSI'] = f"{rsi:.1f} | {rsi_score}分"

    vol_ratio = latest['Volume_Ratio']
    if vol_ratio > 1.5: vol_score = 20
    elif vol_ratio > 1.0: vol_score = 15
    elif vol_ratio > 0.8: vol_score = 10
    else: vol_score = 0
    score += vol_score
    details['成交量'] = f"{vol_ratio:.1f}x | {vol_score}分"

    macd_hist = latest['MACD_Hist']
    macd = latest['MACD']
    if macd_hist > 0 and macd > 0: macd_score = 30
    elif macd_hist > 0: macd_score = 20
    elif macd > 0: macd_score = 10
    else: macd_score = 0
    score += macd_score
    details['MACD'] = f"{macd_hist:.2f} | {macd_score}分"

    price = latest['Close']
    ma20, ma60 = latest['MA20'], latest['MA60']
    bb_upper, bb_lower = latest['BB_Upper'], latest['BB_Lower']

    if price > ma20 > ma60 and price > bb_upper: bb_score = 30
    elif price > ma20 > ma60: bb_score = 25
    elif price > ma20: bb_score = 15
    elif price > bb_lower: bb_score = 10
    else: bb_score = 0
    score += bb_score
    details['均線布林'] = f"價{price:.0f} MA20:{ma20:.0f} | {bb_score}分"

    return score, details, bull_market, etf_mode

def get_advice(score, bull_market, etf_mode):
    if bull_market:
        return "🚀 大多頭確認", "系統關閉。股價 > 年線5% 以上，無腦買入持有"

    if etf_mode:
        if score >= 60: return "💰 偏多買進", "ETF寬鬆模式：60分以上可進場"
        elif score >= 40: return "😐 中性觀望", "40-60分震盪區"
        else: return "⚠️ 偏空小心", "<40分轉弱"
    else:
        if score >= 70: return "💰 偏多買進", "個股嚴格模式：70分以上才進場"
        elif score >= 50: return "😐 中性觀望", "50-70分觀察區"
        else: return "⚠️ 偏空小心", "<50分轉弱"

def backtest(df, ticker):
    bull_market, _, _ = detect_bull_market(df)
    etf_mode = is_etf(ticker)

    if bull_market:
        buy_threshold, sell_threshold = 0, -999
        mode = "大多頭模式"
    elif etf_mode:
        buy_threshold, sell_threshold = 60, 30
        mode = "ETF寬鬆"
    else:
        buy_threshold, sell_threshold = 70, 40
        mode = "個股嚴格"

    scores = []
    for i in range(len(df)):
        if i < 250: scores.append(50)
        else:
            temp_score, _, _, _ = get_score(df.iloc[:i+1], ticker)
            scores.append(temp_score)
    df['Score'] = scores

    position = 0
    trades = []
    equity = [1.0]

    for i in range(1, len(df)):
        price = df['Close'].iloc[i]
        prev_price = df['Close'].iloc[i-1]
        score = df['Score'].iloc[i]

        if bull_market:
            position = 1 # 大多頭強制滿倉
        else:
            if position == 0 and score >= buy_threshold:
                position = 1
                trades.append({'date': df.index[i], 'action': '買', 'price': price, 'score': score})
            elif position == 1 and score < sell_threshold:
                position = 0
                trades.append({'date': df.index[i], 'action': '賣', 'price': price, 'score': score})

        ret = price / prev_price if position == 1 else 1.0
        equity.append(equity[-1] * ret)

    df['Equity'] = equity
    df['BuyHold'] = df['Close'] / df['Close'].iloc[0]
    strategy_return = (equity[-1] - 1) * 100
    buy_hold_return = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100

    wins = sum(1 for i in range(1, len(trades), 2) if i < len(trades) and trades[i]['price'] > trades[i-1]['price'])
    total_trades = len(trades) // 2
    win_rate = wins / total_trades * 100 if total_trades > 0 else 0

    peak = df['Equity'].cummax()
    drawdown = (df['Equity'] - peak) / peak * 100
    max_dd = drawdown.min()

    return {
        'mode': mode,
        'strategy': strategy_return,
        'buy_hold': buy_hold_return,
        'win_rate': win_rate,
        'max_dd': max_dd,
        'trades': trades,
        'df': df
    }

if diagnose_btn or backtest_btn:
    with st.spinner("載入數據中..."):
        hist = get_stock_data(stock)

    if hist is None or len(hist) < 250:
        st.error(f"❌ 數據不足，只有{len(hist) if hist is not None else 0}天，需要250天以上")
        st.stop()

    hist = calculate_indicators(hist)
    score, details, bull_market, etf_mode = get_score(hist, stock)
    advice, reason = get_advice(score, bull_market, etf_mode)

    st.subheader("🎯 診斷總評分")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("總分", f"{score}分", advice)
    with col2: st.metric("模式", "ETF寬鬆" if etf_mode else "個股嚴格")
    with col3: st.metric("牛熊", "大多頭" if bull_market else "震盪/空頭")

    if bull_market:
        st.success("🚀 檢測到大多頭：股價 > 年線5% 以上。系統自動關閉，報酬 = 買入持有")

    with st.expander("📋 五項技術診斷 + Debug"):
        for k, v in details.items():
            st.text(f"{k}: {v}")
        st.info(f"**操作建議**: {reason}")

    if backtest_btn:
        st.subheader("📊 2年歷史回測報告")
        result = backtest(hist, stock)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("模式", result['mode'])
        col2.metric("策略報酬", f"{result['strategy']:.1f}%", f"{result['strategy']-result['buy_hold']:.1f}% vs 大盤")
        col3.metric("買入持有", f"{result['buy_hold']:.1f}%")
        col4.metric("勝率", f"{result['win_rate']:.1f}%", f"最大回檔 {result['max_dd']:.1f}%")

        st.line_chart(result['df'][['Equity', 'BuyHold']].rename(columns={'Equity': '策略淨值', 'BuyHold': '買入持有'}))

        if result['trades']:
            st.caption(f"交易次數: {len(result['trades'])//2} 次")
            trade_df = pd.DataFrame(result['trades'])
            st.dataframe(trade_df.tail(10), use_container_width=True)

else:
    st.info("👆 輸入代號後點擊按鈕開始。L7.3版：Debug年線數值，抓出牛熊誤判原因")
    st.caption("個股70分｜ETF60分｜股價>年線5% = 大多頭模式")
