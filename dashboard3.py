import streamlit as st
import requests

# FastAPI 基本路徑
BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="經濟健康度儀表板", layout="wide")

# --- 1. 定義 API 快取函式 ---

@st.cache_data(ttl=600) # 快取 10 分鐘，避免頻繁請求可用日期
def get_dates():
    try:
        response = requests.get(f"{BASE_URL}/available_dates")
        return response.json() if response.status_code == 200 else []
    except:
        return []

@st.cache_data(ttl=300) # 股價快取 5 分鐘
def fetch_stock_price(symbol):
    """從 FastAPI 獲取單一標的的最新資訊"""
    try:
        # 確保你的 FastAPI 有實作 /stock_price 接口
        res = requests.get(f"{BASE_URL}/stock_price", params={"symbol": symbol})
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        return None
    return None

# --- 2. 頁面標題與股價監控區塊 ---

st.title("📈 經濟健康度儀表板")

st.subheader("美股重點標的 (每 5 分鐘更新)")
target_stocks = ["NVDA", "TSLA", "COST", "BA"] 
stock_cols = st.columns(len(target_stocks))

for i, symbol in enumerate(target_stocks):
    with stock_cols[i]:
        # 使用快取函式獲取數據
        s_data = fetch_stock_price(symbol)
        
        if s_data and "current_price" in s_data:
            st.metric(
                label=s_data["symbol"], 
                value=f"${s_data['current_price']}", 
                delta=f"{s_data['change']}"
            )
        else:
            st.info(f"等待 {symbol} 數據...")

st.divider() # 分隔線

# --- 3. 側邊欄日期選擇 ---

available_dates = get_dates()

st.sidebar.header("查詢條件")
selected_date = st.sidebar.selectbox("請選擇查詢月份", options=available_dates)

# --- 4. 呼叫 API 獲取指定日期的評分 ---

if selected_date:
    # 這裡通常不建議給結果加長效快取，因為使用者可能想看即時計算
    params = {"target_date": selected_date}
    try:
        response = requests.get(f"{BASE_URL}/signal", params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # 呈現數據儀表板
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    label=f"{selected_date} 綜合評分", 
                    value=f"{data['total_score']:.1f}"
                )
            
            with col2:
                signal_light = data["signal"].upper()
                if signal_light == "RED":
                    st.error("🔴 高風險紅燈：通膨或匯率波動劇烈")
                elif signal_light == "YELLOW":
                    st.warning("🟡 警示黃燈：經濟環境出現波動")
                else:
                    st.success("🟢 穩健綠燈：指標處於健康區間")
                    
            # 額外資訊展示
            with st.expander("查看原始數據細節"):
                st.json(data)
        else:
            st.error("無法取得該日期的評分資料，請檢查後端 API。")
    except:
        st.error("連線至 FastAPI 失敗，請確認後端服務已啟動。")
