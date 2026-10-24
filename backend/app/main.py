"""
FastAPI Main Application Entry Point
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.app.database import init_db, SessionLocal
from backend.app.services.seed import seed_initial_data
from backend.app.monitoring.engine import start_monitoring_loop, stop_monitoring_loop
from backend.app.api.websocket import ws_manager

# API Route Routers
from backend.app.api.auth import router as auth_router
from backend.app.api.dashboard import router as dashboard_router
from backend.app.api.services import router as services_router
from backend.app.api.incidents import router as incidents_router
from backend.app.api.recovery import router as recovery_router
from backend.app.api.simulations import router as simulations_router
from backend.app.api.audit import router as audit_router
from backend.app.api.anomalies import router as anomalies_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database & Seed Baseline Data
    print("[Lifecycle] Initializing database tables...")
    init_db()
    
    db = SessionLocal()
    try:
        print("[Lifecycle] Seeding baseline users, microservices, and autonomic policies...")
        seed_initial_data(db)
        print("[Lifecycle] Initializing AI Anomaly Detection model...")
        from backend.app.ml.anomaly_detector import anomaly_detector
        anomaly_detector.train_on_history(db)
    finally:
        db.close()

    # Start background telemetry engine loop
    monitoring_task = asyncio.create_task(start_monitoring_loop())
    
    yield

    # Shutdown: Stop background task cleanly
    stop_monitoring_loop()
    monitoring_task.cancel()
    try:
        await monitoring_task
    except asyncio.CancelledError:
        pass
    print("[Lifecycle] Self-Healing Cloud backend shutdown complete.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomic Self-Healing Cloud System with AI Anomaly Detection and Automated Incident Recovery.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register REST Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(services_router, prefix=settings.API_V1_STR)
app.include_router(incidents_router, prefix=settings.API_V1_STR)
app.include_router(recovery_router, prefix=settings.API_V1_STR)
app.include_router(simulations_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(anomalies_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
def healthcheck():
    """Liveness probe for containers and monitoring agents."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.websocket("/ws/monitoring")
async def websocket_monitoring_endpoint(websocket: WebSocket):
    """Real-time telemetry and self-healing alert streaming channel."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive & accept client ping/pong
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
