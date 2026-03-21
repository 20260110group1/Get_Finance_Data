import streamlit as st
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

# --- 頁面 1: 經濟儀表板 ---
def show_economic_dashboard():
    st.title("📊 經濟健康度儀表板")
    
    @st.cache_data
    def get_dates():
        try:
            response = requests.get(f"{BASE_URL}/available_dates")
            return response.json() if response.status_code == 200 else []
        except: return []

    available_dates = get_dates()
    st.sidebar.header("查詢條件")
    selected_date = st.sidebar.selectbox("請選擇查詢月份", options=available_dates)

    if selected_date:
        params = {"target_date": selected_date}
        res = requests.get(f"{BASE_URL}/signal", params=params)
        if res.status_code == 200:
            data = res.json()
            col1, col2 = st.columns(2)
            with col1: st.metric(label="綜合評分", value=f"{data['total_score']:.1f}")
            with col2:
                sig = data["signal"].upper()
                if sig == "RED": st.error("🔴 高風險紅燈")
                elif sig == "YELLOW": st.warning("🟡 警示黃燈")
                else: st.success("🟢 穩健綠燈")
            with st.expander("詳細數據"): st.json(data)

# --- 頁面 2: 美股新聞 ---
def show_news_dashboard():
    st.title("📰 每日美股精選新聞")
    
    with st.sidebar:
        st.title("新聞面板")
        days = st.slider("幾天內新聞？", 1, 7, 1)
        limit = st.number_input("顯示數量", 5, 50, 10)

    # 呼叫 FastAPI 獲取新聞
    try:
        res = requests.get(f"{BASE_URL}/news", params={"days": days, "limit": limit})
        top_news = res.json() if res.status_code == 200 else []
    except:
        st.error("無法連接新聞 API"); return

    if not top_news:
        st.warning("暫無新聞資料。")
    else:
        for news in top_news:
            with st.container():
                col_s, col_c = st.columns([1, 6])
                col_s.metric("重要性", f"{news['importance_score']:.2f}")
                with col_c:
                    st.subheader(f"[{news['title']}]({news['link']})")
                    c1, c2 = st.columns(2)
                    c1.write(f"🔹 來源: {news['source']}")
                    sent = news['sentiment_score']
                    emoji = "正向" if sent > 0.6 else "中性" if sent > 0.4 else "負向"
                    c2.write(f"🎭 情緒: {emoji} ({sent:.2f})")
                    with st.expander("摘要"): st.write(news['content'])
            st.divider()

# --- 導航主邏輯 ---
st.set_page_config(page_title="金融監控系統", layout="wide")

pg = st.navigation([
    st.Page(show_economic_dashboard, title="經濟健康度", icon="📈"),
    st.Page(show_news_dashboard, title="美股精選新聞", icon="📰"),
])
pg.run()