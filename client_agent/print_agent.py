import os
import json
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configuration
PORT = 1234
DEFAULT_PRINT_DIR = r"C:\print_jobs"

class PrintHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()

    def do_OPTIONS(self):
        # Handle Preflight requests from browser
        self._set_headers()

    def do_GET(self):
        # Health check endpoint
        self._set_headers()
        response = {
            "status": "online",
            "agent": "NY Print Agent",
            "version": "1.0.0",
            "print_dir": DEFAULT_PRINT_DIR
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)

            msg_type = data.get('type', 'print') # 'print' or 'config'
            target_dir = data.get('path') or DEFAULT_PRINT_DIR

            if msg_type == 'config':
                print(f"[{self.date_time_string()}] Configuration updated from Web UI")
                print(f"                      Target Folder: {target_dir}")
                self._set_headers(200)
                self.wfile.write(b"Config Updated")
                return

            xml_content = data.get('xml')
            filename = data.get('filename', 'print_job.xml')

            if not xml_content:
                self._set_headers(400)
                self.wfile.write(b"Missing xml content")
                return

            # Ensure print directory exists
            if not os.path.exists(target_dir):
                try:
                    os.makedirs(target_dir)
                except Exception as e:
                    self._set_headers(500)
                    self.wfile.write(f"Failed to create directory: {str(e)}".encode())
                    return

            # Save the file
            filepath = os.path.join(target_dir, filename)
            # Use .tmp then rename for atomic write (prevent Bartender from reading partial file)
            tmp_path = filepath + ".tmp"
            
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(xml_content)
            
            if os.path.exists(filepath):
                os.remove(filepath)
            os.rename(tmp_path, filepath)

            print(f"[{self.date_time_string()}] Successfully wrote: {filename}")
            print(f"                      To folder: {target_dir}")
            
            self._set_headers(200)
            self.wfile.write(b"Success")
            
        except Exception as e:
            print(f"Error: {str(e)}")
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
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, PrintHandler)
    
    print("-" * 50)
    print(" NY PRINT AGENT - Starting...")
    print(f" Status:    READY")
    print(f" Port:      {PORT}")
    print(f" Local IP:  {get_ip()}")
    print(f" Watch Dir: {DEFAULT_PRINT_DIR}")
    print("-" * 50)
    print("Keep this window open during packing session.")
    print("Press Ctrl+C to stop.")
    
    httpd.serve_forever()

if __name__ == "__main__":
    run()
