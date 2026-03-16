import streamlit as st
import requests

# FastAPI 基本路徑
BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="經濟健康度儀表板", layout="wide")
st.title("經濟健康度儀表板")

# --- 新增：股價監控區塊 ---
st.subheader("美股重點標的")
# 你可以從 get_us_stocks_symbol.py 獲取清單，或手動設定常用標的
target_stocks = ["NVDA", "TSLA", "COST", "BA"] 
stock_cols = st.columns(len(target_stocks))

for i, symbol in enumerate(target_stocks):
    with stock_cols[i]:
        try:
            # 呼叫我們剛剛在 FastAPI 建立的新接口
            res = requests.get(f"{BASE_URL}/stock_price", params={"symbol": symbol})
            if res.status_code == 200:
                s_data = res.json()
                st.metric(
                    label=s_data["symbol"], 
                    value=f"${s_data['current_price']}", 
                    delta=f"{s_data['change']}"
                )
        except:
            st.write(f"{symbol} 載入失敗")

st.divider()

# --- 1. 獲取所有可用日期 (用於下拉選單) ---
@st.cache_data # 增加快取減少 API 負擔
def get_dates():
    response = requests.get(f"{BASE_URL}/available_dates")
    return response.json() if response.status_code == 200 else []

available_dates = get_dates()

# --- 2. 側邊欄日期選擇 ---
st.sidebar.header("查詢條件")
selected_date = st.sidebar.selectbox("請選擇查詢月份", options=available_dates)

# --- 3. 呼叫 API 獲取指定日期的評分 ---
if selected_date:
    # 傳遞參數給 FastAPI，例如：/signal?target_date=2025-01-01
    params = {"target_date": selected_date}
    response = requests.get(f"{BASE_URL}/signal", params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        # --- 4. 呈現數據儀表板 ---
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