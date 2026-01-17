import uvicorn
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.container import Container
from src.core.logger import setup_logging
from src.modules.authorization import router as auth_router


container = Container()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = logging.getLogger(__name__)

    # wiring modules
    container.wire(modules=[
        "src.modules.authorization.router",
        "src.modules.authorization.dependencies"
    ])
    
    db = container.database()
    logger.info("Database instance created")

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


    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])

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
