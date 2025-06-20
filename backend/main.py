import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import add_exception_handlers

from app.dbrm import Engine, Session
from app.dbrm.decorators import create_all_tables
from app.core.startup import startup_background_services, shutdown_background_services

# Configure logging
logs_dir = Path(__file__).parent / "logs"
logs_dir.mkdir(parents=True, exist_ok=True) # Create logs directory if it doesn't exist
log_file_path = logs_dir / "app.log" # Define log file path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(), # Keep console output
        logging.FileHandler(log_file_path) # Add file output
    ]
)
logger = logging.getLogger(__name__)

def init_db():
    try:
        engine = Engine.from_env()       
        with Session(engine) as session:
            created_tables = create_all_tables(session)
            return created_tables
    except Exception as e:
        logger.error(f"Fail to initialize database: {str(e)}")
        return []

@asynccontextmanager
async def startup_db_client(app: FastAPI):
    logger.info("Initializing database...")
    try:
        app.created_tables = init_db()
        if app.created_tables:
            logger.info(f"Database initialized successfully, created tables: {', '.join(app.created_tables)}")
        else:
            logger.warning("Database initialization may not have completed successfully, please check configuration or logs")
        
        # Start background services (earnings scheduler + assignment processor)
        logger.info("Starting background services...")
        startup_background_services()
        logger.info("Background services started successfully")
        
        yield
    except Exception as e:
        logger.error(f"Error occurred during database initialization: {str(e)}")
        logger.warning("Application will continue to start, but database functionality may be unavailable")
        app.created_tables = []
    finally:
        # Stop background services when the app shuts down
        logger.info("Stopping background services...")
        shutdown_background_services()
        logger.info("Background services stopped")

app = FastAPI(
    title="Automobile Maintenance System API",
    description="RESTful API for Automobile Maintenance System",
    version="1.0.0",
    lifespan=startup_db_client
)

# Register the exception handlers from app.core.exceptions
add_exception_handlers(app)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "message": "Welcome to the Automobile Maintenance System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}


if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
