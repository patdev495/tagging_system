import os
import json
import socket
import threading
import time
import logging
import traceback
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

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

    def _create_bt_app(self):
        """Create a new BarTender COM instance, trying multiple strategies."""
        pythoncom.CoInitialize()
        
        # Strategy 1: Standard Dispatch (most reliable for re-attach)
        strategies = [
            ("Standard Dispatch", lambda: win32com.client.Dispatch("BarTender.Application")),
            ("Dynamic Dispatch", lambda: win32com.client.dynamic.Dispatch("BarTender.Application")),
        ]
        
        for name, creator in strategies:
            try:
                app = creator()
                # Verify the object is alive
                _ = app.Formats
                app.Visible = False
                logger.info(f"BarTender connected via {name}")
                return app
            except Exception as e:
                logger.warning(f"{name} failed: {e}")
                continue
        
        # Strategy 3: Kill BarTender and restart fresh
        logger.warning("All Dispatch strategies failed — restarting BarTender process...")
        try:
            import subprocess
            subprocess.run(["taskkill", "/F", "/IM", "bartend.exe"], 
                          capture_output=True, timeout=5)
            time.sleep(2)
        except Exception:
            pass
        
        # Try again after restart
        for name, creator in strategies:
            try:
                app = creator()
                _ = app.Formats
                app.Visible = False
                logger.info(f"BarTender connected via {name} (after restart)")
                return app
            except Exception as e:
                logger.warning(f"{name} after restart failed: {e}")
                continue
        
        raise RuntimeError("Could not connect to BarTender after all attempts")

    def start(self):
        if not HAS_PYWIN32:
            logger.error("pywin32 not installed. BarTender Automation unavailable.")
            return False
            
        try:
            logger.info("Initializing BarTender Engine (Direct COM)...")
            self.bt_app = self._create_bt_app()
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
            # Quick health check
            _ = self.bt_app.Formats
        except Exception:
            logger.warning("BarTender COM instance lost. Reconnecting...")
            self.bt_app = self._create_bt_app()

    def _check_printer_status(self, printer_name):
        """Check Windows printer status via win32print API.
        Returns error string if printer has issues, None if OK."""
        try:
            import win32print
            
            # Open printer handle
            hPrinter = win32print.OpenPrinter(printer_name)
            try:
                # GetPrinter level 2 returns detailed info including status
                info = win32print.GetPrinter(hPrinter, 2)
                status = info.get('Status', 0)
                
                # Windows Printer Status Flags
                # https://learn.microsoft.com/en-us/windows/win32/printdocs/printer-info-2
                STATUS_FLAGS = {
                    0x00000001: "Paused",
                    0x00000002: "Error",
                    0x00000004: "Pending Deletion",
                    0x00000008: "Paper Jam",
                    0x00000010: "Paper Out",
                    0x00000020: "Manual Feed Required",
                    0x00000040: "Paper Problem",
                    0x00000080: "Offline",
                    0x00000200: "Not Available",
                    0x00000400: "No Toner",
                    0x00040000: "Out of Memory",
                    0x00080000: "Door Open",
                    0x00100000: "Server Unknown",
                    0x00200000: "Power Save",
                }
                
                if status != 0:
                    issues = []
                    for flag, desc in STATUS_FLAGS.items():
                        if status & flag:
                            issues.append(desc)
                    
                    if issues:
                        error_msg = f"Printer '{printer_name}': {', '.join(issues)}"
                        logger.error(f"Printer status check FAILED: {error_msg} (raw: 0x{status:08X})")
                        return f"Printer Error: {', '.join(issues)}"
                    
                return None  # Printer is OK
            finally:
                win32print.ClosePrinter(hPrinter)
                
        except ImportError:
            logger.warning("win32print not available, skipping printer status check")
            return None
        except Exception as e:
            logger.warning(f"Could not check printer '{printer_name}': {e}")
            return None  # Don't block printing if status check fails

    def _wait_for_print_complete(self, printer_name, timeout=15):
        """Wait for print spooler to finish and check for errors.
        Returns error string if issues found, None if OK."""
        try:
            import win32print
            
            # Poll printer status for up to `timeout` seconds
            for i in range(timeout * 2):  # Check every 0.5s
                time.sleep(0.5)
                
                try:
                    hPrinter = win32print.OpenPrinter(printer_name)
                    try:
                        info = win32print.GetPrinter(hPrinter, 2)
                        status = info.get('Status', 0)
                        
                        # Check for error flags
                        ERROR_FLAGS = {
                            0x00000002: "Error",
                            0x00000008: "Paper Jam",
                            0x00000010: "Paper Out",
                            0x00000040: "Paper Problem",
                            0x00000080: "Offline",
                            0x00000400: "No Toner",
                            0x00080000: "Door Open",
                        }
                        
                        issues = []
                        for flag, desc in ERROR_FLAGS.items():
                            if status & flag:
                                issues.append(desc)
                        
                        if issues:
                            return f"Printer Error: {', '.join(issues)}"
                        
                        # Check if there are still jobs in queue
                        jobs = win32print.EnumJobs(hPrinter, 0, 10, 1)
                        if not jobs:
                            # No more jobs, printer is idle — success
                            return None
                            
                        # Check if any job has error status
                        for job in jobs:
                            job_status = job.get('Status', 0)
                            # JOB_STATUS_ERROR = 0x02, JOB_STATUS_OFFLINE = 0x20
                            # JOB_STATUS_PAPEROUT = 0x40, JOB_STATUS_BLOCKED_DEVQ = 0x200
                            if job_status & 0x02:
                                return f"Print Job Error (Status: 0x{job_status:04X})"
                            if job_status & 0x40:
                                return "Printer Error: Paper Out"
                            if job_status & 0x20:
                                return "Printer Error: Offline"
                                
                    finally:
                        win32print.ClosePrinter(hPrinter)
                except Exception as e:
                    logger.warning(f"Spooler check #{i}: {e}")
            
            # Timeout reached without error — assume OK
            return None
            
        except ImportError:
            return None
        except Exception as e:
            logger.warning(f"Print completion check failed: {e}")
            return None

    def print_xml(self, xml_content, printer_name_override=None):
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

                # Priority 1: printer_name_override from JSON request
                # Priority 2: Extract from XML
                printer_name = printer_name_override
                if not printer_name:
                    printer_element = print_element.find('.//Printer')
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

                # Force background/silent mode before every print
                try:
                    self.bt_app.Visible = False
                except Exception:
                    pass
                try:
                    # Suppress any interactive dialogs
                    self.bt_app.SuppressErrorDialog = True
                    self.bt_app.SuppressSaveDialog = True
                except Exception:
                    pass

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

                if (printer_name and printer_name.strip()):
                    try:
                        # Pre-validate with win32print for better error reporting
                        try:
                            import win32print
                            h_printer = win32print.OpenPrinter(printer_name)
                            win32print.ClosePrinter(h_printer)
                        except Exception:
                             return f"Error: Printer '{printer_name}' not found on this system. Please check Windows Printers list."

                        # Attempt to set in BarTender
                        bt_format.PrintSetup.Printer = printer_name
                    except Exception as pe:
                        logger.error(f"Could not set printer '{printer_name}': {pe}")
                        return f"Error: Cannot use printer '{printer_name}'. Check if it's connected and online."
                
                # Use SetNamedSubString on the Format object
                for key, val in substrings.items():
                    try:
                        bt_format.SetNamedSubStringValue(key, str(val))
                    except Exception as nse:
                        logger.warning(f"Could not set named substring '{key}': {nse}")
                
                # ------- Pre-print: Check printer hardware status -------
                actual_printer = printer_name
                if not actual_printer:
                    try:
                        actual_printer = bt_format.PrintSetup.Printer
                    except Exception:
                        pass
                
                if actual_printer:
                    hw_err = self._check_printer_status(actual_printer)
                    if hw_err:
                        try:
                            bt_format.Close(0)
                        except Exception:
                            pass
                        return hw_err
                    
                # ------- Silent Print -------
                status_msg = "Success"
                try:
                    # PrintOut(ShowPrintDialog, ShowProgressDialog)
                    # Both False = fully silent, no UI
                    bt_format.PrintOut(False, False)
                except Exception as po_err:
                    logger.error(f"PrintOut failed: {po_err}")
                    status_msg = f"Print Failed: {po_err}"
                
                # Post-print: Wait briefly then check printer for errors
                if status_msg == "Success" and actual_printer:
                    # Monitor spooler for job completion & errors
                    post_status = self._wait_for_print_complete(actual_printer, timeout=15)
                    if post_status:
                        logger.error(f"Post-print error: {post_status}")
                        status_msg = post_status
                
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
        try:
            self._set_headers(200, 'application/json')
            response = {
                "status": "online",
                "bt_initialized": bt_engine.is_initialized,
                "version": "1.2.0"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except (ConnectionAbortedError, ConnectionResetError):
            pass # Client closed connection, ignore
        except Exception as e:
            logger.error(f"GET Error: {e}")

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
            logger.info(f"START Print Job: {filename} (Printer: {data.get('printer_name') or 'Default'})")
            bt_status = bt_engine.print_xml(xml_content, printer_name_override=data.get('printer_name'))
            
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
    httpd = ThreadingHTTPServer(server_address, PrintHandler)
    
    logger.info(f"NY PRINT AGENT v1.2.0 starting on {get_ip()}:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping agent...")
        httpd.server_close()

if __name__ == "__main__":
    run()
