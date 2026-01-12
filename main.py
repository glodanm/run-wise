import uvicorn
import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.container import Container
from src.core.logger import setup_logging


container = Container()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = logging.getLogger(__name__)

    # wiring modules
    container.wire(modules=[])

    from src.core.database import Base
    
    try:
        db = container.database()
        logger.info("Database instance created")
        
        async with db.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise

    yield

    # Shutdown
    try:
        await db.engine.dispose()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error during database shutdown: {e}", exc_info=True)
    finally:
        container.unwire()


def create_app() -> FastAPI:
    app = FastAPI(title="RunWise", lifespan=lifespan)
    
    logger = logging.getLogger("RunWise")
    logger.debug("Service started")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"],
        reload_excludes=["*.pyc", "__pycache__"],
        reload_delay=1.0
    )

