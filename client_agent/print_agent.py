import os
import json
import socket
import threading
import time
import logging
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler

# Only import pywin32 on Windows
try:
    import win32com.client
    from win32com.client import gencache
    import pythoncom
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False

# Configuration
PORT = 1234
DEFAULT_PRINT_DIR = r"C:\print_jobs"
LOG_FILE = "agent_activity.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PrintAgent")

class BarTenderEngine:
    def __init__(self):
        self.bt_app = None
        self._lock = threading.Lock()
        self.is_initialized = False

    def start(self):
        if not HAS_PYWIN32:
            logger.error("pywin32 not installed. BarTender Automation unavailable.")
            return False
            
        try:
            logger.info("Initializing BarTender Engine (Direct COM)...")
            pythoncom.CoInitialize()
            
            try:
                import win32com.client.dynamic
                self.bt_app = win32com.client.dynamic.Dispatch("BarTender.Application")
            except Exception as inner_e:
                logger.error(f"Dynamic Dispatch failed: {inner_e}")
                self.bt_app = win32com.client.Dispatch("BarTender.Application")
                
            try:
                # Rigorous check: accessing Version and Formats collection
                _ = self.bt_app.Version
                _ = self.bt_app.Formats
                self.bt_app.Visible = False
            except Exception as prop_e:
                logger.warning(f"Initial property set warning: {prop_e}")
                
            self.is_initialized = True
            logger.info("BarTender Engine: READY (Background Mode)")
            return True
        except Exception as e:
            logger.critical(f"Failed to start BarTender: {e}")
            self.is_initialized = False
            return False

    def _ensure_connected(self):
        """Ensure COM connection is alive and healthy."""
        try:
            # Check most basic properties
            _ = self.bt_app.Version
            _ = self.bt_app.Formats
        except Exception:
            logger.warning("BarTender COM instance lost or unresponsive. Re-attaching...")
            pythoncom.CoInitialize()
            try:
                import win32com.client.dynamic
                self.bt_app = win32com.client.dynamic.Dispatch("BarTender.Application")
                try:
                    self.bt_app.Visible = False
                except Exception:
                    pass
            except Exception as e:
                logger.error(f"Critical: Failed to re-attach BarTender: {e}")
                raise

    def print_xml(self, xml_content):
        if not self.is_initialized:
            return "Error: BarTender engine not initialized."
        
        with self._lock:
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(xml_content)
                print_element = root.find('.//Print')
                if print_element is None:
                    return "Error: No <Print> element found in XML"
                
                format_element = print_element.find('Format')
                if format_element is None or not format_element.text:
                    return "Error: No <Format> path found in XML"
                format_path = format_element.text
                
                if not os.path.exists(format_path):
                    return f"Error: Template file not found: {format_path}"

                printer_name = None
                printer_element = print_element.find('.//PrintSetup/Printer')
                if printer_element is not None and printer_element.text:
                    printer_name = printer_element.text

                substrings = {}
                for ns in print_element.findall('NamedSubString'):
                    name = ns.get('Name')
                    value_element = ns.find('Value')
                    if name and value_element is not None:
                        substrings[name] = value_element.text

                pythoncom.CoInitialize()
                
                try:
                    self._ensure_connected()
                except Exception as conn_err:
                    return f"Error connecting to BarTender: {conn_err}"

                # Open Format with Retry (Formats.Open is the standard BarTender COM API)
                bt_format = None
                last_err = ""
                for attempt in range(3):
                    try:
                        logger.info(f"Opening template (Attempt {attempt+1}): {format_path}")
                        bt_format = self.bt_app.Formats.Open(format_path, False, "")
                        if bt_format: break
                    except Exception:
                        exc_data = traceback.format_exc()
                        last_err = f"{exc_data}"
                        logger.warning(f"Formats.Open attempt {attempt+1} failed. Trace:\n{exc_data}")
                        try:
                            self._ensure_connected()
                            time.sleep(1) # Wait a bit for BarTender to settle
                        except:
                            pass
                
                if not bt_format:
                    return f"Error: Formats.Open failed after 3 attempts. Details: {last_err.splitlines()[-1]}"

                if printer_name:
                    try:
                        bt_format.PrintSetup.Printer = printer_name
                    except Exception as pe:
                        logger.warning(f"Could not set printer '{printer_name}': {pe}")
                
                # Use SetNamedSubString on the Format object
                for key, val in substrings.items():
                    try:
                        bt_format.SetNamedSubStringValue(key, str(val))
                    except Exception as nse:
                        logger.warning(f"Could not set named substring '{key}': {nse}")
                    
                # Print with verification
                status_msg = "Success"
                try:
                    bt_format.PrintOut(False, False)
                except Exception as e:
                    logger.error(f"PrintOut failed: {e}")
                    status_msg = f"PrintOut Failed: {e}"
                
                try:
                    bt_format.Close(0) # btDoNotSaveChanges
                except Exception:
                    pass
                return status_msg
                
            except Exception as e:
                return f"Internal Error: {str(e)}"
            finally:
                pythoncom.CoUninitialize()

bt_engine = BarTenderEngine()

class PrintHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type='text/plain'):
        self.send_response(status)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', content_type)
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        self._set_headers(200, 'application/json')
        response = {
            "status": "online",
            "bt_initialized": bt_engine.is_initialized,
            "version": "1.2.0"
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)

            msg_type = data.get('type', 'print')
            target_dir = data.get('path') or DEFAULT_PRINT_DIR
            
            if msg_type == 'config':
                logger.info(f"Config Update: Folder set to {target_dir}")
                self._set_headers(200)
                self.wfile.write(b"OK")
                return

            xml_content = data.get('xml')
            filename = data.get('filename', "job.xml")

            if not xml_content:
                self._set_headers(400)
                self.wfile.write(b"No XML")
                return

            # 1. Direct Print
            logger.info(f"START Print Job: {filename}")
            bt_status = bt_engine.print_xml(xml_content)
            
            if "Success" in bt_status:
                logger.info(f"PRINT SUCCESS: {filename}")
            else:
                logger.error(f"PRINT FAILED: {filename} - {bt_status}")

            # 2. Log XML to File
            try:
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                filepath = os.path.join(target_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(xml_content)
                logger.info(f"XML LOGGED: {filepath}")
            except Exception as fe:
                logger.error(f"FILE LOG FAILED: {fe}")

            self._set_headers(200)
            self.wfile.write(bt_status.encode('utf-8'))
            
        except Exception as e:
            logger.error(f"System Error: {e}")
            self._set_headers(500)
            self.wfile.write(str(e).encode('utf-8'))

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def run():
    bt_engine.start()
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, PrintHandler)
    
    logger.info(f"NY PRINT AGENT v1.2.0 starting on {get_ip()}:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping agent...")
        httpd.server_close()

if __name__ == "__main__":
    run()
