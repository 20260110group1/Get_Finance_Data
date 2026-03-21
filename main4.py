from fastapi import FastAPI, Query
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, DateTime, Text, desc
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Optional
from datetime import datetime, timedelta

app = FastAPI()

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

class NewsArticle(Base):
    __tablename__ = "news_articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    link = Column(String(500), unique=True)
    source = Column(String(50))
    content = Column(Text)
    sentiment_score = Column(Float)
    importance_score = Column(Float)
    published = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)

# 自動建立所有不存在的資料表 (包含 news_articles)
Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "API running"}

# --- 經濟分數 API ---
@app.get("/available_dates")
def get_available_dates():
    db = SessionLocal()
    try:
        results = db.query(EconomicScore.score_date).distinct().order_by(EconomicScore.score_date.desc()).all()
        return [str(r.score_date) for r in results]
    finally:
        db.close()

@app.get("/signal")
def get_signal(target_date: Optional[str] = None):
    db = SessionLocal()
    try:
        query = db.query(EconomicScore)
        if target_date:
            result = query.filter(EconomicScore.score_date == target_date).first()
        else:
            result = query.order_by(EconomicScore.score_date.desc()).first()
        
        if not result: return {"message": "no data found"}
        return {
            "date": result.score_date, "cpi_score": result.cpi_score,
            "ppi_score": result.ppi_score, "fx_score": result.fx_score,
            "total_score": result.total_score, "signal": result.signal_light
        }
    finally:
        db.close()

# --- 新增：新聞資料 API ---
@app.get("/news")
def get_news(days: int = 1, limit: int = 10):
    db = SessionLocal()
    try:
        time_threshold = datetime.now() - timedelta(days=days)
        # 篩選時間、按重要性排序
        articles = db.query(NewsArticle)\
            .filter(NewsArticle.created_at >= time_threshold)\
            .order_by(desc(NewsArticle.importance_score))\
            .limit(limit).all()
        return articles
    finally:
        db.close()