from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.core.config import settings
from app.core.exceptions import (
    AlreadyExistsError,
    BusinessRuleError,
    DomainError,
    InsufficientStockError,
    NotFoundError,
)

app = FastAPI(title="Le Bon Coin", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Routers never raise HTTPException. Services raise the domain errors below and
# this table is the single place where they become HTTP status codes.
_STATUS_BY_ERROR: dict[type[DomainError], int] = {
    NotFoundError: 404,
    AlreadyExistsError: 409,
    InsufficientStockError: 409,
    BusinessRuleError: 422,
}


async def domain_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Translate a business exception into the HTTP status bound to its class."""
    if not isinstance(exc, DomainError):  # pragma: no cover - registered per class above
        raise exc
    return JSONResponse(
        status_code=_STATUS_BY_ERROR[type(exc)],
        content={"detail": exc.message},
    )


for error_type in _STATUS_BY_ERROR:
    app.add_exception_handler(error_type, domain_error_handler)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe, used by the Docker healthcheck and by CI."""
    return {"status": "ok"}


# --- Frontend statique -------------------------------------------------------
# Présent seulement dans l'image : en développement, Vite sert le frontend.

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

# Segments que le catch-all ne doit jamais servir, sinon GET /products/ renvoie
# index.html en 200 au lieu d'un 404. À compléter à chaque nouveau routeur.
_API_SEGMENTS = frozenset(
    {"products", "carts", "orders", "health", "docs", "redoc", "openapi.json"}
)

if _STATIC_DIR.is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=_STATIC_DIR / "assets"),
        name="assets",
    )

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str) -> FileResponse:
        """Serve a built asset, or index.html so react-router handles the route."""
        if full_path.split("/", 1)[0] in _API_SEGMENTS:
            raise NotFoundError("Cette ressource n'existe pas.")

        candidate = (_STATIC_DIR / full_path).resolve()
        # A crafted path such as ../../etc/passwd must not escape the build.
        if full_path and candidate.is_file() and candidate.is_relative_to(_STATIC_DIR):
            return FileResponse(candidate)
        return FileResponse(_STATIC_DIR / "index.html")
