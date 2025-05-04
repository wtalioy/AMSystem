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

from app.dbrm import Engine, Session
from app.dbrm.decorators import create_all_tables

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
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
        yield
    except Exception as e:
        logger.error(f"Error occurred during database initialization: {str(e)}")
        logger.warning("Application will continue to start, but database functionality may be unavailable")
        app.created_tables = []

app = FastAPI(title="Automobile Maintenance System API", lifespan=startup_db_client)

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
    return {"message": "Welcome to the Automobile Maintenance System API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
