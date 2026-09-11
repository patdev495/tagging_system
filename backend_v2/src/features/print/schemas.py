from pydantic import BaseModel
from typing import Optional, List

class CartonStatusUpdate(BaseModel):
    status: str # SUCCESS or FAILED

class TemplateInfo(BaseModel):
    name: str
    path: str
    size_bytes: int
    updated_at: str

class TemplateListResponse(BaseModel):
    templates: List[TemplateInfo]

class TemplateValidateRequest(BaseModel):
    template_name: str
    folder: Optional[str] = None

class TemplateValidateResponse(BaseModel):
    valid: bool
    message: str
    resolved_path: Optional[str] = None

class CanonicalTemplateItem(BaseModel):
    filename: str
    customer: str
    type: str
    name: str
    exists: bool = False
    resolved_path: Optional[str] = None

class CanonicalTemplatesResponse(BaseModel):
    templates: List[CanonicalTemplateItem]
    templates_dir: str

class EngineRestartResponse(BaseModel):
    success: bool
    message: str
    bartender_ready: bool
