"""Global exception handlers."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI) -> None:
    """Register unified exception handlers."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        request_id = getattr(request.state, "request_id", None)
        detail = exc.detail if isinstance(exc.detail, str) else "Request failed."
        if not request.url.path.startswith("/api/v1"):
            return JSONResponse(status_code=exc.status_code, content={"detail": detail})
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": f"http_{exc.status_code}",
                "error_message": detail,
                "request_id": request_id,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", None)
        if not request.url.path.startswith("/api/v1"):
            return JSONResponse(status_code=500, content={"detail": str(exc)})
        return JSONResponse(
            status_code=500,
            content={
                "error_code": "internal_error",
                "error_message": str(exc),
                "request_id": request_id,
            },
        )
