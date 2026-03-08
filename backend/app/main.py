from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.config import settings
from app.auth.router import router as auth_router
from app.market_data.router import router as market_data_router
from app.clients.router import router as clients_router
from app.goals.router import router as goals_router
from app.risk_profiler.router import router as risk_profiler_router
from app.pdf.router import router as pdf_router
from app.scenarios.router import router as scenarios_router
from app.admin.router import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.jobs.scheduler import start, stop
    start()
    try:
        yield
    finally:
        stop()


app = FastAPI(title="India Investment Analyzer", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(market_data_router)
app.include_router(clients_router)
app.include_router(goals_router)
app.include_router(risk_profiler_router)
app.include_router(pdf_router)
app.include_router(scenarios_router)
app.include_router(admin_router)


@app.get("/health")
def health_check():
    from app.db.base import engine
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "error"

    from app.jobs.scheduler import scheduler
    sched_status = "running" if scheduler.running else "stopped"

    return {"status": "ok", "db": db_status, "scheduler": sched_status}
