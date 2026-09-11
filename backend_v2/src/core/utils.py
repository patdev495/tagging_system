"""
Core Utility Functions — Unified and robust system helpers.
Encapsulates Template Path Resolution and Environment Detection.
"""
import os
import sys
from typing import Optional
from src.core.config import settings

class TemplateResolver:
    """
    Unified template resolver for BarTender BTW files.
    Acts as the Single Source of Truth for path resolution and template search strategies.
    Supports both backend server execution and client-side print agent execution.
    """
    DEFAULT_TEMPLATES_DIR = "D:\\PAT\\Templates"
    CANONICAL_TEMPLATE_MAP = {
        "a11_tem2": "a11_02.btw",
        "a11": "a11.btw",
        "standard": "carton_base.btw",
        "detailed": "carton_detail.btw",
    }

    @classmethod
    def get_canonical_template_filename(cls, template_type: Optional[str]) -> str:
        """Return canonical BarTender template filename (.btw) for a template_type."""
        normalized_type = (template_type or "standard").strip().lower()
        return cls.CANONICAL_TEMPLATE_MAP.get(normalized_type, "carton_base.btw")

    @classmethod
    def check_template_exists(cls, template_name_or_path: str, custom_dir: Optional[str] = None) -> dict:
        """Verify whether a template file exists in the given directory or standard directories."""
        filename = os.path.basename(template_name_or_path)
        root = cls.get_execution_root()
        search_dirs = []
        if custom_dir:
            search_dirs.append(os.path.normpath(custom_dir))
        search_dirs.extend([
            os.path.normpath(cls.DEFAULT_TEMPLATES_DIR),
            os.path.normpath(os.path.join(root, getattr(settings, 'LABEL_TEMPLATES_DIR', 'resources/templates'))),
            os.path.normpath(os.path.join(root, 'resources', 'templates')),
            os.path.normpath(root),
        ])

        for d in search_dirs:
            candidate = os.path.normpath(os.path.join(d, filename))
            if os.path.exists(candidate):
                return {"exists": True, "path": candidate, "searched_dirs": search_dirs}

        return {"exists": False, "path": None, "searched_dirs": search_dirs}

    @staticmethod
    def get_execution_root() -> str:
        """Determines the correct execution root directory, handling PyInstaller environments."""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        
        # Dev mode safe root detection
        cwd = os.getcwd()
        if os.path.exists(os.path.join(cwd, "main.py")) or os.path.exists(os.path.join(cwd, "src")):
            return cwd
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    @classmethod
    def resolve(cls, path: Optional[str], fallback_path: Optional[str] = None, local_dir: Optional[str] = None, default_filename: str = "carton.ui.btw") -> str:
        """
        Resolves a BTW template path using structured search strategies.
        Checks local directory overrides first, then database settings, then resource fallback directories.
        """
        root = cls.get_execution_root()
        
        # Strategy 1: Prioritize local directory override if provided by client (remap)
        if local_dir and path:
            filename = os.path.basename(path)
            local_path = os.path.normpath(os.path.join(local_dir, filename))
            if os.path.exists(local_path):
                return local_path

        # Strategy 2: Check standard DEFAULT_TEMPLATES_DIR (e.g. D:\PAT\Templates)
        if path:
            filename = os.path.basename(path)
            standard_path = os.path.normpath(os.path.join(cls.DEFAULT_TEMPLATES_DIR, filename))
            if os.path.exists(standard_path):
                return standard_path
            
        def evaluate_path(p: Optional[str]) -> Optional[str]:
            if not p:
                return None
            
            # If absolute path, verify existence and return
            if os.path.isabs(p) or (":" in p and "\\" in p):
                norm = os.path.normpath(p)
                if os.path.exists(norm):
                    return norm
                return None
                
            # Strategy 2: Check relative to settings template directory
            templates_dir = getattr(settings, 'LABEL_TEMPLATES_DIR', 'resources/templates')
            path1 = os.path.normpath(os.path.join(root, templates_dir, p))
            if os.path.exists(path1):
                return path1
                
            # Strategy 3: Check relative to execution root directly
            path2 = os.path.normpath(os.path.join(root, p))
            if os.path.exists(path2):
                return path2
                
            return None

        # Check primary path
        resolved = evaluate_path(path)
        if resolved:
            return resolved
            
        # Check fallback path
        if fallback_path:
            resolved = evaluate_path(fallback_path)
            if resolved:
                return resolved

        # Final absolute fallback path if nothing exists (safety net)
        fallback_dir = getattr(settings, 'LABEL_TEMPLATES_DIR', 'resources/templates')
        final_path = os.path.normpath(os.path.join(root, fallback_dir, os.path.basename(path or fallback_path or default_filename)))
        return final_path


# --- Backward Compatible Thin Wrappers ---

def get_backend_root() -> str:
    """Get backend execution root directory."""
    return TemplateResolver.get_execution_root()

def resolve_template_path(primary_path: Optional[str] = None, fallback_path: Optional[str] = None) -> str:
    """Resolve BarTender label template path."""
    return TemplateResolver.resolve(primary_path, fallback_path)
