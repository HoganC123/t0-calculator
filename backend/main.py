from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, journal, trade

app = FastAPI(
    title="A股散户工具平台",
    description="A股 T+0 辅助工具后端 API",
    version="0.1.0",
)

# ── CORS（开发阶段允许所有来源）────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 路由 ──────────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(trade.router)
app.include_router(journal.router)


# ── 健康检查 ──────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health():
    """专用健康检查端点，供前端预热 Railway 冷启动使用。"""
    return {"status": "ok"}
