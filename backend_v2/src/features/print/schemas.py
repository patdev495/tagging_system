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

class TemplateValidateResponse(BaseModel):
    valid: bool
    message: str
    resolved_path: Optional[str] = None

class EngineRestartResponse(BaseModel):
    success: bool
    message: str
    bartender_ready: bool
