"""
BarTender Engine — Tích hợp trực tiếp vào Backend.
Quản lý COM connection tới BarTender, in tem, xuất PDF.
"""
import os
import json
import time
import logging
import threading
import traceback
import subprocess
from src.core.config import settings

logger = logging.getLogger("BarTenderEngine")

# Import pywin32 — chỉ chạy trên Windows
try:
    import win32com.client
    import pythoncom
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False
    logger.warning("pywin32 not installed. BarTender Automation unavailable.")


class BarTenderEngine:
    """Singleton engine quản lý kết nối COM tới BarTender."""

    def __init__(self):
        self.bt_app = None
        self._lock = threading.Lock()
        self.is_initialized = False

    def _create_bt_app(self):
        """Tạo COM instance mới, thử nhiều chiến thuật."""
        pythoncom.CoInitialize()

        strategies = [
            ("Standard Dispatch", lambda: win32com.client.Dispatch("BarTender.Application")),
            ("Dynamic Dispatch", lambda: win32com.client.dynamic.Dispatch("BarTender.Application")),
        ]

        for name, creator in strategies:
            try:
                app = creator()
                _ = app.Formats
                app.Visible = False
                logger.info(f"BarTender connected via {name}")
                return app
            except Exception as e:
                logger.warning(f"{name} failed: {e}")

        # Fallback: Kill & restart BarTender
        logger.warning("All Dispatch strategies failed — restarting BarTender process...")
        try:
            subprocess.run(["taskkill", "/F", "/IM", "bartend.exe"],
                           capture_output=True, timeout=5)
            time.sleep(2)
        except Exception:
            pass

        for name, creator in strategies:
            try:
                app = creator()
                _ = app.Formats
                app.Visible = False
                logger.info(f"BarTender connected via {name} (after restart)")
                return app
            except Exception as e:
                logger.warning(f"{name} after restart failed: {e}")

        raise RuntimeError("Could not connect to BarTender after all attempts")

    def start(self):
        """Khởi tạo kết nối COM tới BarTender."""
        if not HAS_PYWIN32:
            logger.error("pywin32 not installed. BarTender unavailable.")
            return False
        try:
            logger.info("Initializing BarTender Engine...")
            self.bt_app = self._create_bt_app()
            self.is_initialized = True
            logger.info("BarTender Engine: READY")
            return True
        except Exception as e:
            logger.critical(f"Failed to start BarTender: {e}")
            self.is_initialized = False
            return False

    def _ensure_connected(self):
        """Kiểm tra COM connection còn sống không, nếu mất thì reconnect."""
        try:
            _ = self.bt_app.Formats
        except Exception:
            logger.warning("BarTender COM instance lost. Reconnecting...")
            self.bt_app = self._create_bt_app()

    def _check_printer_status(self, printer_name):
        """Kiểm tra trạng thái máy in qua win32print."""
        try:
            import win32print
            hPrinter = win32print.OpenPrinter(printer_name)
            try:
                info = win32print.GetPrinter(hPrinter, 2)
                status = info.get('Status', 0)
                STATUS_FLAGS = {
                    0x00000001: "Paused", 0x00000002: "Error",
                    0x00000008: "Paper Jam", 0x00000010: "Paper Out",
                    0x00000040: "Paper Problem", 0x00000080: "Offline",
                    0x00000400: "No Toner", 0x00080000: "Door Open",
                }
                if status != 0:
                    issues = [desc for flag, desc in STATUS_FLAGS.items() if status & flag]
                    if issues:
                        return f"Printer Error: {', '.join(issues)}"
                return None
            finally:
                win32print.ClosePrinter(hPrinter)
        except Exception:
            return None

    # ──────────────────────────────────────────────
    # PRINT XML
    # ──────────────────────────────────────────────
    def print_xml(self, xml_content: str, printer_name_override: str = None, fallback_path: str = None) -> dict:
        """
        In tem từ BTXML. Trả về dict: {"success": bool, "message": str, "type": "print"|"pdf", "data": str|None}
        """
        if not self.is_initialized:
            return {"success": False, "message": "BarTender engine not initialized."}

        with self._lock:
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(xml_content)
                print_element = root.find('.//Print')
                if print_element is None:
                    return {"success": False, "message": "No <Print> element found in XML"}

                format_element = print_element.find('Format')
                if format_element is None or not format_element.text:
                    return {"success": False, "message": "No <Format> path found in XML"}
                format_path = format_element.text
                
                # [FIX] Nếu đường dẫn không tồn tại hoặc là đường dẫn tương đối, thử tìm trong thư mục resources
                if not format_path or not os.path.isabs(format_path) or not os.path.exists(format_path):
                    from src.core.utils import get_backend_root
                    from src.core.config import settings
                    
                    filename = os.path.basename(format_path) if format_path else "carton.ui.btw"
                    alt_path = os.path.join(get_backend_root(), settings.LABEL_TEMPLATES_DIR, filename)
                    
                    if os.path.exists(alt_path):
                        logger.info(f"Resolved relative path '{format_path}' to '{alt_path}'")
                        format_path = alt_path
                    elif fallback_path and os.path.exists(fallback_path):
                        logger.info(f"Template not found, using fallback: {fallback_path}")
                        format_path = fallback_path
                    else:
                        return {"success": False, "message": f"Template file not found: {format_path} (Checked also {alt_path})"}

                # Printer name
                printer_name = printer_name_override
                if not printer_name:
                    printer_el = print_element.find('.//Printer')
                    if printer_el is not None and printer_el.text:
                        printer_name = printer_el.text

                # Named substrings
                substrings = {}
                for ns in print_element.findall('NamedSubString'):
                    name = ns.get('Name')
                    value_el = ns.find('Value')
                    if name and value_el is not None:
                        substrings[name] = value_el.text

                pythoncom.CoInitialize()
                try:
                    self._ensure_connected()
                except Exception as conn_err:
                    return {"success": False, "message": f"Error connecting to BarTender: {conn_err}"}

                # Open Format (retry 3 lần)
                bt_format = None
                last_err = ""
                for attempt in range(3):
                    try:
                        bt_format = self.bt_app.Formats.Open(format_path, False, "")
                        if bt_format:
                            break
                    except Exception:
                        last_err = traceback.format_exc()
                        self._ensure_connected()
                        time.sleep(1)

                if not bt_format:
                    return {"success": False, "message": f"Formats.Open failed: {last_err.splitlines()[-1]}"}

                # Set substrings
                for key, val in substrings.items():
                    try:
                        bt_format.SetNamedSubStringValue(key, str(val))
                    except Exception:
                        pass

                # ──── PDF Export ────
                if printer_name and (
                    printer_name.upper() == "PDF"
                    or ("PDF" in printer_name.upper() and "MICROSOFT" not in printer_name.upper())
                ):
                    logger.info("PDF Export requested.")
                    return self._export_to_pdf(bt_format)

                # ──── Physical Print ────
                if printer_name:
                    bt_format.PrintSetup.Printer = printer_name

                try:
                    bt_format.PrintOut(False, False)
                    result = {"success": True, "message": "Success", "type": "print"}
                except Exception as po_err:
                    result = {"success": False, "message": f"Print Failed: {po_err}"}

                try:
                    bt_format.Close(0)
                except Exception:
                    pass
                return result

            except Exception as e:
                return {"success": False, "message": f"Internal Error: {str(e)}"}
            finally:
                pythoncom.CoUninitialize()

    # ──────────────────────────────────────────────
    # PDF EXPORT (tự động xử lý hộp thoại Save)
    # ──────────────────────────────────────────────
    def _export_to_pdf(self, bt_format) -> dict:
        """In qua Microsoft Print to PDF + auto-handle Save dialog."""
        import base64
        import uuid

        if hasattr(settings, 'PDF_EXPORT_DIR') and settings.PDF_EXPORT_DIR:
            temp_dir = settings.PDF_EXPORT_DIR
        else:
            temp_dir = os.path.join(os.environ.get('TEMP', 'C:\\temp'), 'ny_labels')
            
        os.makedirs(temp_dir, exist_ok=True)
        uid = str(uuid.uuid4())[:8]
        temp_pdf = os.path.join(temp_dir, f"label_{uid}.pdf")

        def auto_save_dialog(target_path, timeout=15):
            import win32gui
            import win32con

            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    def find_save_dialog(hwnd, results):
                        if win32gui.IsWindowVisible(hwnd):
                            title = win32gui.GetWindowText(hwnd)
                            if "save" in title.lower() and (
                                "print" in title.lower() or "output" in title.lower() or "pdf" in title.lower()
                            ):
                                results.append(hwnd)
                        return True

                    results = []
                    win32gui.EnumWindows(find_save_dialog, results)

                    if results:
                        hwnd = results[0]
                        logger.info(f"Found Save dialog: {win32gui.GetWindowText(hwnd)}")

                        def find_edit(parent):
                            edits = []
                            def callback(h, _):
                                cls = win32gui.GetClassName(h)
                                if cls in ('Edit', 'ComboBoxEx32'):
                                    edits.append(h)
                                return True
                            win32gui.EnumChildWindows(parent, callback, None)
                            return edits

                        edits = find_edit(hwnd)
                        if edits:
                            for edit_hwnd in edits:
                                cls = win32gui.GetClassName(edit_hwnd)
                                if cls == 'Edit':
                                    win32gui.SendMessage(edit_hwnd, win32con.WM_SETTEXT, 0, target_path)
                                    break
                                elif cls == 'ComboBoxEx32':
                                    inner = win32gui.FindWindowEx(edit_hwnd, 0, 'ComboBox', None)
                                    if inner:
                                        ie = win32gui.FindWindowEx(inner, 0, 'Edit', None)
                                        if ie:
                                            win32gui.SendMessage(ie, win32con.WM_SETTEXT, 0, target_path)
                                            break
                                    ie = win32gui.FindWindowEx(edit_hwnd, 0, 'Edit', None)
                                    if ie:
                                        win32gui.SendMessage(ie, win32con.WM_SETTEXT, 0, target_path)
                                        break

                            time.sleep(0.3)

                            def find_save_button(parent):
                                buttons = []
                                def callback(h, _):
                                    if win32gui.GetClassName(h) == 'Button':
                                        text = win32gui.GetWindowText(h)
                                        if text in ('&Save', 'Save', '&Lưu', 'Lưu', 'OK', '&OK'):
                                            buttons.append(h)
                                    return True
                                win32gui.EnumChildWindows(parent, callback, None)
                                return buttons

                            buttons = find_save_button(hwnd)
                            if buttons:
                                win32gui.SendMessage(buttons[0], win32con.BM_CLICK, 0, 0)
                                logger.info("Auto-clicked Save button")
                                time.sleep(0.5)
                                # Handle overwrite confirmation
                                cr = []
                                win32gui.EnumWindows(find_save_dialog, cr)
                                for ch in cr:
                                    cbtns = find_save_button(ch)
                                    if cbtns:
                                        win32gui.SendMessage(cbtns[0], win32con.BM_CLICK, 0, 0)
                                return True
                except Exception as e:
                    logger.warning(f"Dialog handler error: {e}")
                time.sleep(0.3)
            return False

        try:
            bt_format.PrintSetup.Printer = "Microsoft Print to PDF"

            dialog_thread = threading.Thread(target=auto_save_dialog, args=(temp_pdf,), daemon=True)
            dialog_thread.start()

            bt_format.PrintOut(False, False)
            dialog_thread.join(timeout=20)

            # Chờ file PDF ghi xong
            wait_start = time.time()
            while time.time() - wait_start < 10:
                if os.path.exists(temp_pdf) and os.path.getsize(temp_pdf) > 100:
                    time.sleep(0.5)
                    break
                time.sleep(0.3)

            if os.path.exists(temp_pdf) and os.path.getsize(temp_pdf) > 100:
                with open(temp_pdf, "rb") as f:
                    pdf_base64 = base64.b64encode(f.read()).decode('utf-8')
                logger.info(f"PDF created successfully: {os.path.getsize(temp_pdf)} bytes")
                return {"success": True, "message": "Success", "type": "pdf", "data": pdf_base64}
            else:
                return {"success": False, "message": "PDF file was not created."}

        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            return {"success": False, "message": f"PDF export failed - {str(e)}"}
        finally:
            try:
                bt_format.Close(0)
            except Exception:
                pass
            def cleanup():
                time.sleep(2)
                try:
                    if os.path.exists(temp_pdf):
                        os.remove(temp_pdf)
                except Exception:
                    pass
            threading.Thread(target=cleanup, daemon=True).start()

    # ──────────────────────────────────────────────
    # PRINTERS LIST
    # ──────────────────────────────────────────────
    def get_printers(self) -> list:
        """Lấy danh sách máy in Windows (lọc bỏ máy in ảo)."""
        printers = []
        try:
            result = subprocess.run(
                ['powershell', '-Command',
                 'Get-Printer | Select-Object Name, DriverName, PortName, PrinterStatus | ConvertTo-Json'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                if isinstance(data, dict):
                    data = [data]
                skip_names = ["microsoft print to pdf", "microsoft xps", "fax", "onenote", "send to onenote"]
                for p in data:
                    name = p.get("Name", "")
                    if any(s in name.lower() for s in skip_names):
                        continue
                    printers.append({
                        "name": name,
                        "driver": p.get("DriverName", ""),
                        "port": p.get("PortName", ""),
                        "status": p.get("PrinterStatus", 0)
                    })
        except Exception as e:
            logger.warning(f"Failed to enumerate printers: {e}")

        # Thêm tùy chọn PDF ảo
        printers.insert(0, {
            "name": "PDF",
            "driver": "Internal Export",
            "port": "Virtual",
            "status": 0
        })
        return printers


# ──────────────────────────────────────────────
# Singleton instance — khởi tạo khi import
# ──────────────────────────────────────────────
bt_engine = BarTenderEngine()
