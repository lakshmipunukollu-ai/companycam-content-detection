import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base
from app.routers import health, auth, projects, photos, corrections, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and upload directory
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield
    # Shutdown: nothing to clean up


app = FastAPI(
    title="CompanyCam Content Detection API",
    description="Intelligent content detection for construction photos using CV+LLM pipeline",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount upload directory for serving images
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(photos.router)
app.include_router(corrections.router)
app.include_router(reports.router)
