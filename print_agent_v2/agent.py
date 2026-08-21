import os
import json
import logging
import subprocess
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel
import xml.etree.ElementTree as ET

# Import the unified COM app singleton
from bartender_com import bt_com_app

# Import Scale Manager
try:
    from scale.manager import scale_manager
except ImportError:
    from .scale.manager import scale_manager

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PrintAgent")

app = FastAPI(title="NY Print Agent V2 (Unified COM & Scale Engine)")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize BarTender and Scale on startup
@app.on_event("startup")
def startup_event():
    logger.info("Starting up Print Agent...")
    success = bt_com_app.start()
    if success:
        logger.info("BarTender COM Engine successfully started on agent.")
    else:
        logger.warning("BarTender COM Engine failed to start on agent. Will retry lazily on print jobs.")
    
    try:
        scale_manager.load_config()
        scale_manager.start()
        logger.info("Scale Manager successfully initialized.")
    except Exception as e:
        logger.warning(f"Scale Manager initialization notice: {e}")

@app.on_event("shutdown")
def shutdown_event():
    logger.info("Shutting down Print Agent...")
    try:
        scale_manager.stop()
    except Exception:
        pass

# === Schemas ===
class PrintRequest(BaseModel):
    xml_content: str
    printer_name: Optional[str] = None
    local_template_dir: Optional[str] = None

class ScaleConfigRequest(BaseModel):
    port: Optional[str] = None
    baudrate: Optional[int] = None
    hotkey: Optional[str] = None
    auto_connect: Optional[bool] = None

# === Endpoints ===

@app.get("/status")
def get_status():
    return {
        "status": "online", 
        "mode": "COM", 
        "version": "2.3.0",
        "bartender_ready": bt_com_app.is_initialized,
        "scale_status": scale_manager.get_status()
    }

@app.get("/printers")
def get_printers():
    """Lấy danh sách máy in từ hệ thống"""
    printers_list = bt_com_app.get_printers()
    return [p["name"] for p in printers_list]

@app.get("/check-dir")
def check_directory(path: str = ""):
    logger.info(f"Checking directory: {path}")
    normalized_path = os.path.normpath(path)
    exists = os.path.exists(normalized_path) and os.path.isdir(normalized_path)
    return {"exists": exists, "path": normalized_path}

@app.get("/check-file")
def check_file(folder: str, filename: str):
    full_path = os.path.normpath(os.path.join(folder, filename))
    exists = os.path.exists(full_path) and os.path.isfile(full_path)
    return {"exists": exists, "path": full_path}

# === Scale Endpoints ===

@app.get("/scale/status")
def get_scale_status():
    """Lấy trạng thái kết nối cổng COM cân điện tử"""
    return scale_manager.get_status()

@app.get("/scale/current")
def get_scale_current():
    """Lấy trọng lượng và cờ ổn định thời gian thực từ cân"""
    return scale_manager.get_current_reading()

@app.post("/scale/tare")
def trigger_scale_tare():
    """Gửi lệnh trừ bì tới cân"""
    success = scale_manager.tare()
    return {"success": success}

@app.post("/scale/zero")
def trigger_scale_zero():
    """Gửi lệnh zero tới cân"""
    success = scale_manager.zero()
    return {"success": success}

@app.post("/scale/config")
def update_scale_config(cfg: ScaleConfigRequest):
    """Cập nhật cấu hình cổng COM, baudrate, và hotkey của cân"""
    port_changed = False
    if cfg.port and cfg.port != scale_manager._port:
        scale_manager._port = cfg.port
        port_changed = True
    if cfg.baudrate and cfg.baudrate != scale_manager._baudrate:
        scale_manager._baudrate = cfg.baudrate
        port_changed = True
    if cfg.hotkey:
        scale_manager._hotkey = cfg.hotkey
    if cfg.auto_connect is not None:
        scale_manager._auto_connect = cfg.auto_connect
    
    scale_manager.save_config()
    if port_changed:
        scale_manager.reconnect()
    return {"success": True, "config": scale_manager.get_status()}

@app.post("/print")
async def process_print(req: PrintRequest):
    try:
        content = req.xml_content
        
        result = await run_in_threadpool(
            bt_com_app.print_xml,
            xml_content=content, 
            printer_name_override=req.printer_name,
            local_template_dir=req.local_template_dir
        )
        
        if result["success"]:
            return {
                "success": True, 
                "message": result.get("message", "Print job processed via COM"),
                "type": result.get("type"),
                "data": result.get("data")
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "Print failure"))
        
    except HTTPException: raise
    except Exception as e:
        logger.error(f"Print agent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import argparse
    import sys
    
    # Determine execution directory (handles both python running and compiled .exe)
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
        
    config_path = os.path.join(application_path, "config.json")
    
    default_port = 8080
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                if "port" in config_data:
                    default_port = int(config_data["port"])
        except Exception as e:
            logger.warning(f"Failed to read config.json: {e}")
    
    parser = argparse.ArgumentParser(description="NY Print Agent")
    parser.add_argument("--port", type=int, default=default_port, help=f"Port to run the agent on (default: {default_port})")
    args = parser.parse_args()
    
    logger.info(f"Starting Print Agent on port {args.port}...")
    uvicorn.run(app, host="0.0.0.0", port=args.port)
