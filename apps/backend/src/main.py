from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import api_router
from .database import init_db, close_db
from .config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = get_settings()
    await init_db()
    yield
    # Shutdown
    await close_db()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Strategy Lab MCP",
        description="Visual platform for trading strategy research and backtesting with MCP integration",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health")
    async def health_check():
        return {"status": "ok", "service": "strategy-lab-backend"}

    @app.get("/")
    async def root():
        return {
            "name": "Strategy Lab MCP",
            "version": "0.1.0",
            "docs": "/docs",
            "mcp": "/api/v1/mcp/tools",
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.api_workers,
    )