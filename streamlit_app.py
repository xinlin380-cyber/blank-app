import requests
from datetime import datetime, timedelta

@st.cache_data(ttl=3600)
def get_stock_data(stock_code):
    stock = stock_code.replace('.TW','').replace('.TWO','').strip()
    df = pd.DataFrame()
    市場別 = ""

    # 1. 先試上市.TW
    try:
        ticker = f"{stock}.TW"
        df = yf.download(ticker, period="2y", progress=False, auto_adjust=True)
        if not df.empty and len(df) > 20:
            市場別 = "上市"
    except: pass

    # 2. 上市沒有就試上櫃.TWO
    if df.empty:
        try:
            ticker = f"{stock}.TWO"
            df = yf.download(ticker, period="2y", progress=False, auto_adjust=True)
            if not df.empty and len(df) > 20:
                市場別 = "上櫃"
        except: pass

    # 3. 都沒有就直接打 FinMind API 抓興櫃，不用裝套件
    if df.empty:
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
            url = "https://api.finmindtrade.com/api/v4/data"
            params = {
                "dataset": "TaiwanStockPrice",
                "data_id": stock,
                "start_date": start_date,
                "end_date": end_date
            }
            res = requests.get(url, params=params, timeout=10)
            data = res.json()
            if data['status'] == 200 and data['data']:
                df = pd.DataFrame(data['data'])
                df = df.rename(columns={'date':'Date','open':'Open','max':'High','min':'Low','close':'Close','Trading_Volume':'Volume'})
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.set_index('Date').sort_index()
                市場別 = "興櫃"
        except Exception as e:
            st.warning(f"興櫃資料抓取失敗: {e}")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df.dropna(), 市場別
