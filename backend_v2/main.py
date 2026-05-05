import os
import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
import uvicorn

# Configure logging to show debug info in console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)

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

    # --- Serve Frontend Production Build ---
    # Determine frontend dist path
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    frontend_dist = os.path.join(base_path, "frontend_v2", "dist")
    
    # If running as PyInstaller EXE, check relative to the EXE location
    if getattr(sys, 'frozen', False):
        exe_base = os.path.dirname(sys.executable)
        prod_frontend_dist = os.path.abspath(os.path.join(exe_base, "..", "frontend_v2", "dist"))
        if os.path.exists(prod_frontend_dist):
            frontend_dist = prod_frontend_dist

    if os.path.exists(frontend_dist):
        from fastapi.staticfiles import StaticFiles
        # Mount at "/" with html=True:
        # - Starlette checks routes BEFORE mounts, so API routes always win
        # - html=True serves index.html for directory requests (SPA support)
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
    
    @app.on_event("startup")
    def startup_bartender():
        """Khởi tạo BarTender Engine khi Backend start."""
        try:
            from src.features.print.bartender_engine import bt_engine
            bt_engine.start()
        except Exception as e:
            import logging
            logging.getLogger("main").error(f"BarTender init failed: {e}")

    @app.get("/api/v1/health", tags=["Health"])
    def health_check():
        from src.features.print.bartender_engine import bt_engine
        return {
            "status": "ok", 
            "version": "v2.0",
            "bartender": "ready" if bt_engine.is_initialized else "offline"
        }

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    from src.core.config import settings
    
    # Check if running as EXE
    is_prod = getattr(sys, 'frozen', False)
    
    if is_prod:
        # In production EXE, pass the app object directly
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=settings.API_PORT, 
            reload=False
        )
    else:
        # In development, use string to support reload
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=settings.API_PORT, 
            reload=True
        )
