import os
import sys
from src.core.config import settings

def get_backend_root():
    """Lấy thư mục gốc của backend (chứa src hoặc exe)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    
    # Cách an toàn hơn để lấy root: tìm thư mục chứa file main.py hoặc thư mục hiện tại
    # Giả sử cấu hình chuẩn là chạy từ thư mục backend_v2
    cwd = os.getcwd()
    if os.path.exists(os.path.join(cwd, "main.py")) or os.path.exists(os.path.join(cwd, "src")):
        return cwd
        
    # Fallback về logic cũ nếu không chạy từ root
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def resolve_template_path(primary_path: str = None, fallback_path: str = None) -> str:
    root = get_backend_root()
    
    def get_abs(p):
        if not p: return None
        if os.path.isabs(p) or (":" in p and "\\" in p):
            return os.path.normpath(p)
            
        # Thử theo LABEL_TEMPLATES_DIR
        path1 = os.path.join(root, settings.LABEL_TEMPLATES_DIR, p)
        if os.path.exists(path1):
            return os.path.normpath(path1)
            
        # Thử theo ROOT
        path2 = os.path.join(root, p)
        if os.path.exists(path2):
            return os.path.normpath(path2)
            
        return os.path.normpath(path1)

    # Logic tìm kiếm
    final_path = None
    if primary_path:
        abs_p = get_abs(primary_path)
        if os.path.exists(abs_p):
            final_path = abs_p
            
    if not final_path and fallback_path:
        abs_f = get_abs(fallback_path)
        if os.path.exists(abs_f):
            final_path = abs_f
            
    if not final_path:
        # Fallback cuối cùng
        final_path = get_abs(primary_path or fallback_path or "carton.ui.btw")

    print(f"[DEBUG] Resolve Template: primary={primary_path}, fallback={fallback_path} -> RESULT: {final_path}")
    return final_path


