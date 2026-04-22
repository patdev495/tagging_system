from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
import uvicorn

from src.core.config import settings
from src.core.exceptions import custom_http_exception_handler
from src.features.customer.router import router as customer_router
from src.features.product.router import router as product_router
from src.features.history.router import router as history_router
from src.features.box.router import router as box_router
from src.features.print.router import router as print_router

def create_app() -> FastAPI:
    app = FastAPI(title="NY Tagging System V2", version="2.0.0")

    # Global exception handler
    app.add_exception_handler(HTTPException, custom_http_exception_handler)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(customer_router, prefix="/api/v1")
    app.include_router(product_router, prefix="/api/v1")
    app.include_router(history_router, prefix="/api/v1")
    app.include_router(box_router, prefix="/api/v1")
    app.include_router(print_router, prefix="/api/v1")

    @app.get("/api/v1/health", tags=["Health"])
    def health_check():
        return {"status": "ok", "version": "v2.0"}

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.API_PORT, reload=True)
