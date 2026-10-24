from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from .config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="UK Wind Forecast Monitor",
        description="Day-ahead wind forecasts vs actuals (Elexon BMRS), January 2026.",
        version="1.0.0",
    )
    app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins), allow_methods=["GET"], allow_headers=["*"])
    app.include_router(router)
    return app


app = create_app()
