import os
import json
import uuid
import time
import logging
import subprocess
import threading
import xml.etree.ElementTree as ET
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import win32com
try:
    import win32com.client
    import pythoncom
except ImportError:
    print("Error: pywin32 not installed. Please run 'uv pip install pywin32'")

# Cấu hình Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PrintAgent")

app = FastAPI(title="NY Print Agent V2 (COM)")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Schemas ===
class PrintRequest(BaseModel):
    xml_content: str
    printer_name: Optional[str] = None
    local_template_dir: Optional[str] = None

# === BarTender COM Manager ===
class BarTenderManager:
    def __init__(self):
        self.bt_app = None
        self._lock = threading.Lock()

    def get_app(self):
        with self._lock:
            if self.bt_app is None:
                pythoncom.CoInitialize()
                try:
                    logger.info("Initializing BarTender COM Application...")
                    self.bt_app = win32com.client.Dispatch("BarTender.Application")
                    self.bt_app.Visible = False
                    logger.info("BarTender COM Initialized successfully.")
                except Exception as e:
                    logger.error(f"Failed to initialize BarTender COM: {e}")
                    self.bt_app = None
            return self.bt_app

    def print_xml(self, xml_content: str, printer_name: str = None):
        bt = self.get_app()
        if not bt:
            raise Exception("BarTender not available.")
        
        with self._lock:
            try:
                root = ET.fromstring(xml_content)
                
                # 1. Trích xuất đường dẫn File Tem
                format_node = root.find(".//Format")
                if format_node is None or not format_node.text:
                    raise Exception("No <Format> tag found in XML")
                format_path = format_node.text
                
                # 2. Trích xuất tên Máy In
                if not printer_name:
                    printer_node = root.find(".//Printer")
                    if printer_node is not None and printer_node.text:
                        printer_name = printer_node.text
                
                # 3. Trích xuất Dữ liệu (NamedSubStrings)
                substrings = {}
                for ns in root.findall('.//NamedSubString'):
                    name = ns.get('Name')
                    value_el = ns.find('Value')
                    if name and value_el is not None:
                        substrings[name] = value_el.text
                        
                logger.info(f"COM Print Task - Template: {format_path}, Printer: {printer_name}")
                
                # 4. Thực thi in qua COM Object Model
                bt_format = None
                try:
                    bt_format = bt.Formats.Open(format_path, False, "")
                    if not bt_format:
                        raise Exception(f"Failed to open format: {format_path}")
                    
                    # Điền dữ liệu
                    for key, val in substrings.items():
                        try:
                            bt_format.SetNamedSubStringValue(key, str(val))
                        except Exception as e:
                            logger.warning(f"Failed to set substring {key}: {e}")
                    
                    # Chọn máy in
                    if printer_name:
                        bt_format.PrintSetup.Printer = printer_name
                        
                    # Ra lệnh in
                    logger.info("Calling PrintOut...")
                    bt_format.PrintOut(False, False)
                    logger.info("PrintOut success.")
                finally:
                    if bt_format:
                        try:
                            bt_format.Close(0)
                        except: pass
                        
            except Exception as e:
                logger.error(f"COM Print Error: {e}")
                raise e
                
            return True

bt_manager = BarTenderManager()

# === Endpoints ===

@app.get("/status")
def get_status():
    return {"status": "online", "mode": "COM", "version": "2.1.0"}

@app.get("/printers")
def get_printers():
    """Lấy danh sách máy in từ hệ thống"""
    try:
        cmd = ["powershell", "-Command", "Get-Printer | Select-Object Name | ConvertTo-Json"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if isinstance(data, dict): return [data['Name']]
            return [p['Name'] for p in data]
    except: pass
    return []

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
        
        # 1. Remap path
        if req.local_template_dir:
            try:
                root = ET.fromstring(content)
                formats = root.findall(".//Format")
                for fmt in formats:
                    if fmt.text:
                        filename = os.path.basename(fmt.text)
                        new_path = os.path.normpath(os.path.join(req.local_template_dir, filename))
                        if not os.path.exists(new_path):
                            raise HTTPException(status_code=404, detail=f"File tem không tồn tại: {new_path}")
                        fmt.text = new_path
                content = ET.tostring(root, encoding='utf-8').decode('utf-8')
            except HTTPException: raise
            except: pass

        # 2. In qua COM
        bt_manager.print_xml(content, req.printer_name)
        
        return {"success": True, "message": "Print job processed via COM"}
        
    except Exception as e:
        logger.error(f"Print error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import argparse
    import json
    import sys
    
    # Xác định thư mục chạy thực tế (hỗ trợ cả file .py và file .exe)
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
    
    logger.info(f"Starting Agent on port {args.port}...")
    uvicorn.run(app, host="0.0.0.0", port=args.port)
