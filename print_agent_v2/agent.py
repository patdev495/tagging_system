import os
import json
import logging
import subprocess
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import xml.etree.ElementTree as ET

# Import the unified COM app singleton
from bartender_com import bt_com_app

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PrintAgent")

app = FastAPI(title="NY Print Agent V2 (Unified COM)")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize BarTender on startup
@app.on_event("startup")
def startup_event():
    logger.info("Starting up Print Agent...")
    success = bt_com_app.start()
    if success:
        logger.info("BarTender COM Engine successfully started on agent.")
    else:
        logger.warning("BarTender COM Engine failed to start on agent. Will retry lazily on print jobs.")

# === Schemas ===
class PrintRequest(BaseModel):
    xml_content: str
    printer_name: Optional[str] = None
    local_template_dir: Optional[str] = None

# === Endpoints ===

@app.get("/status")
def get_status():
    return {
        "status": "online", 
        "mode": "COM", 
        "version": "2.2.0",
        "bartender_ready": bt_com_app.is_initialized
    }

@app.get("/printers")
def get_printers():
    """Lấy danh sách máy in từ hệ thống"""
    # Use the unified native Win32 printer enumeration
    printers_list = bt_com_app.get_printers()
    # Return flat list of names for compatibility with frontend expectations
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

@app.post("/print")
async def process_print(req: PrintRequest):
    try:
        content = req.xml_content
        
        # In qua Unified COM module với hỗ trợ phân giải đường dẫn tem tự động
        result = bt_com_app.print_xml(
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
