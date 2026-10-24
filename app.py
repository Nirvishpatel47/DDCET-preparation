import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from database.db import init_db, get_db
from routes.api_questions import router as questions_router
from routes.api_practice import router as practice_router
from routes.api_revision import router as revision_router
from routes.api_import_export import router as import_export_router
from routes.api_analytics import router as analytics_router
from routes.api_settings import router as settings_router
from services.import_export_service import SAMPLE_DEMO_QUESTIONS, process_import
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app = FastAPI(
    title="DDCET Gujarat Exam Preparation System",
    description="Offline-first adaptive preparation application for Gujarat DDCET",
    version="1.0.0"
)

# Enable CORS for local use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include Routers
app.include_router(questions_router)
app.include_router(practice_router)
app.include_router(revision_router)
app.include_router(import_export_router)
app.include_router(analytics_router)
app.include_router(settings_router)


# Initialize database schema and configuration defaults on module load and startup
init_db()

@app.on_event("startup")
def on_startup():
    """Initializes SQLite schema and configuration defaults on application start."""
    init_db()


@app.get("/", response_class=HTMLResponse)
def index():
    """Renders main offline-first single page UI."""
    index_file = os.path.join(TEMPLATES_DIR, "index.html")
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()


@app.post("/api/load-sample-demo")
def load_sample_demo():
    """
    Optional helper to populate the separate sample demonstration questions
    clearly marked as sample data so the student can immediately test all workflows.
    """
    raw_bytes = json.dumps(SAMPLE_DEMO_QUESTIONS).encode("utf-8")
    result = process_import(raw_bytes, "sample_demo.json", preview_only=False)
    return {
        "status": "success",
        "message": "Sample demonstration questions loaded successfully.",
        "result": result
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
