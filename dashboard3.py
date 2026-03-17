import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="經濟健康度儀表板", layout="wide")

# --- 1. 定義 API 快取函式 ---

@st.cache_data(ttl=600)
def get_dates():
    try:
        response = requests.get(f"{BASE_URL}/available_dates", timeout=5)
        return response.json() if response.status_code == 200 else []
    except:
        return []

@st.cache_data(ttl=300)
def fetch_stock_price(symbol):
    try:
        res = requests.get(f"{BASE_URL}/stock_price", params={"symbol": symbol}, timeout=5)
        if res.status_code == 200:
            return res.json()
    except:
        return None
    return None

# --- 2. 頁面標題與介面 ---

st.title("經濟健康度儀表板")

st.subheader("美股重點標的 (每 5 分鐘更新)")
target_stocks = ["NVDA", "TSLA", "COST", "BA"] 
stock_cols = st.columns(len(target_stocks))

for i, symbol in enumerate(target_stocks):
    with stock_cols[i]:
        s_data = fetch_stock_price(symbol)
        if s_data and "current_price" in s_data:
            st.metric(
                label=s_data["symbol"], 
                value=f"${s_data['current_price']}", 
                delta=f"{s_data['change']}"
            )
        else:
            st.info(f"等待 {symbol} 數據...")

st.divider()

# --- 3. 側邊欄與資料查詢 ---

available_dates = get_dates()
st.sidebar.header("查詢條件")
selected_date = st.sidebar.selectbox("請選擇查詢月份", options=available_dates)

if selected_date:
    params = {"target_date": selected_date}
    try:
        response = requests.get(f"{BASE_URL}/signal", params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label=f"{selected_date} 綜合評分", value=f"{data.get('total_score', 0):.1f}")
            with col2:
                signal_light = data.get("signal", "RED").upper()
                if signal_light == "RED":
                    st.error("🔴 高風險紅燈")
                elif signal_light == "YELLOW":
                    st.warning("🟡 警示黃燈")
                else:
                    st.success("🟢 穩健綠燈")
            with st.expander("查看原始數據細節"):
                st.json(data)
    except:
        st.error("連線至 FastAPI 失敗，請確認後端服務已啟動。")
