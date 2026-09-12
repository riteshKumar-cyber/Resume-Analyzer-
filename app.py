from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import settings
from routers import analyze
from utils.helpers import logger, CustomAppException

# Initialize FastAPI Application
app = FastAPI(
    title="Resume Analyzer",
    description="PDF Resume Analyzer built with FastAPI and Jinja2.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup Base Directories
BASE_DIR = settings.BASE_DIR
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Ensure directories exist
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# Mount Static Files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Configure Jinja2 Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include API Routers
app.include_router(analyze.router)


# Custom Exception Handlers
@app.exception_handler(CustomAppException)
async def custom_app_exception_handler(request: Request, exc: CustomAppException):
    """Handle application specific exceptions cleanly for JSON API requests."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle standard HTTP exceptions."""
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.detail
            }
        )
    # For HTML pages, let standard FastAPI error response handle or render
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Invalid request parameter or missing file.",
            "details": exc.errors()
        }
    )


@app.get("/", response_class=HTMLResponse, summary="Serve Web Interface")
async def render_homepage(request: Request):
    """
    Renders the main single-page resume analyzer application interface.
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "max_file_size_mb": settings.MAX_UPLOAD_SIZE_MB
        }
    )


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting Resume Analyzer server at http://{settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
