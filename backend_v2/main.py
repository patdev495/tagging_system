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
from src.features.job_order.router import router as job_order_router

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
    app.include_router(job_order_router, prefix="/api/v1")


    @app.get("/api/v1/health", tags=["Health"])
    def health_check():
        from src.features.print.bartender_engine import bt_engine
        return {
            "status": "ok", 
            "version": "v2.0",
            "bartender": "ready" if bt_engine.is_initialized else "offline"
        }

    # --- Serve Frontend Production Build ---
    # In Docker, we will copy frontend build to a 'static' folder inside backend_v2
    frontend_dist = os.path.join(os.path.dirname(__file__), "static")
    
    # If not in Docker (local dev with production build), check the old path
    if not os.path.exists(frontend_dist):
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        frontend_dist = os.path.join(base_path, "frontend_v2", "dist")

    if os.path.exists(frontend_dist):
        from fastapi.staticfiles import StaticFiles
        from fastapi.responses import FileResponse
        
        # Mount assets specifically first (if they exist in a subfolder)
        assets_path = os.path.join(frontend_dist, "assets")
        if os.path.exists(assets_path):
            app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

        # Catch-all route for SPA:
        # This will serve index.html for any request that isn't handled by API routers
        @app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            # Check if requested path is a file in frontend_dist
            file_path = os.path.join(frontend_dist, full_path)
            if os.path.isfile(file_path):
                return FileResponse(file_path)
            # Otherwise return index.html for SPA routing
            return FileResponse(os.path.join(frontend_dist, "index.html"))
    else:
        logging.getLogger("main").warning(f"Frontend dist not found at {frontend_dist}")
    
    @app.on_event("startup")
    def startup_event():
        """Khởi tạo các dịch vụ khi Backend start."""
        # 1. Khởi tạo Database
        try:
            from src.core.database import init_db
            init_db()
        except Exception as e:
            logging.getLogger("main").error(f"Database init failed: {e}")

        # 2. Khởi tạo BarTender Engine
        try:
            from src.features.print.bartender_engine import bt_engine
            bt_engine.start()
        except Exception as e:
            logging.getLogger("main").error(f"BarTender init failed: {e}")

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    from src.core.config import settings
    
    # Check if running as EXE
    is_prod = getattr(sys, 'frozen', False)
    
    # Use PORT from environment for Render
    port = int(os.environ.get("PORT", settings.API_PORT))
    
    if is_prod:
        # In production EXE, pass the app object directly
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port, 
            reload=False
        )
    else:
        # In development, use string to support reload
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=port, 
            reload=True
        )
