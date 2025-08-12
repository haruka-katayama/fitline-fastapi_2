# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ルーターのインポート（修正版）
from app.routers import (
    health, ui, fitbit, healthplanet, 
    weight, meals, coaching, cron, debug
)

app = FastAPI(
    title="FitLine API",
    description="Fitness tracking and coaching application with multi-device support",
    version="2.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(health.router)
app.include_router(ui.router)
app.include_router(fitbit.router, prefix="/fitbit")
app.include_router(healthplanet.router)  # prefixは内部で設定済み
app.include_router(weight.router)        # prefixは内部で設定済み
app.include_router(meals.router, prefix="/meals")
app.include_router(coaching.router, prefix="/coach")
app.include_router(cron.router, prefix="/cron")
app.include_router(debug.router, prefix="/debug")

@app.get("/")
def root():
    """ルートエンドポイント"""
    return {
        "message": "FitLine API v2.0",
        "services": ["fitbit", "healthplanet", "meals", "coaching"],
        "status": "healthy"
    }
