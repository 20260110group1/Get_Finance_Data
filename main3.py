from fastapi import FastAPI, Query # 增加 Query 用於參數處理
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Float, String, Date
from typing import Optional # 用於定義選擇性參數
import yfinance as yf

app = FastAPI()

@app.get("/stock_price")
def get_stock_price(symbol: str = "AAPL"):
    # 這裡可以根據你的 get_us_stock_price.py 邏輯改寫
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1mo") # 取得近一個月數據
    if hist.empty:
        return {"error": "找不到該標的"}
    
    # 轉換為 dict 格式回傳給 Streamlit
    latest_price = hist['Close'].iloc[-1]
    prev_price = hist['Close'].iloc[-2]
    return {
        "symbol": symbol,
        "current_price": round(latest_price, 2),
        "change": round(latest_price - prev_price, 2)
    }

# 1. 建立 MySQL 連線
DATABASE_URL = "mysql+pymysql://root:密碼@localhost/macro_monitor"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. 建立資料表 model
class EconomicScore(Base):
    __tablename__ = "economic_score"
    id = Column(Integer, primary_key=True, index=True)
    score_date = Column(Date)
    cpi_score = Column(Float)
    ppi_score = Column(Float)
    fx_score = Column(Float)
    total_score = Column(Float)
    signal_light = Column(String(10))

# 3. 測試 API 是否啟動
@app.get("/")
def home():
    return {"message": "API running"}

# --- 新增：獲取所有可用日期清單 ---
@app.get("/available_dates")
def get_available_dates():
    db = SessionLocal()
    try:
        # 查詢所有不重複的日期，並由新到舊排序
        results = db.query(EconomicScore.score_date)\
                   .distinct()\
                   .order_by(EconomicScore.score_date.desc())\
                   .all()
        # 將結果轉換為字串清單回傳 [ "2025-01-01", "2024-12-01", ... ]
        return [str(r.score_date) for r in results]
    finally:
        db.close()

# --- 修改：支援特定日期查詢的 /signal ---
@app.get("/signal")
def get_signal(target_date: Optional[str] = None):
    db = SessionLocal()
    try:
        query = db.query(EconomicScore)
        
        if target_date:
            # 如果有提供日期，查詢該特定日期
            result = query.filter(EconomicScore.score_date == target_date).first()
        else:
            # 如果沒提供日期，維持原樣查詢最新一筆
            result = query.order_by(EconomicScore.score_date.desc()).first()

        if result is None:
            return {"message": "no data found for the specified date"}

        return {
            "date": result.score_date,
            "cpi_score": result.cpi_score,
            "ppi_score": result.ppi_score,
            "fx_score": result.fx_score,
            "total_score": result.total_score,
            "signal": result.signal_light
        }
    finally:
        db.close() # 確保每次查詢後都會關閉連線，避免佔用資料庫資源