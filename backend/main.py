"""FastAPI application entry point.

Creates the FastAPI app, configures CORS, includes routers,
and auto-creates database tables on startup.
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.todos import router as todos_router
from db.database import Base, engine

# Auto-create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todo API",
    description="Todo List Application — Backend REST API",
    version="1.0.0",
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(todos_router, prefix="/api", tags=["todos"])


@app.get("/")
def root():
    """Root endpoint — health info."""
    return {"message": "Todo API is running"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
