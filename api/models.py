from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class InvestigationRequest(BaseModel):
    scenario_id: str
    max_iterations: int = 15
    max_tool_calls: int = 20
    is_synthetic: bool = False

class InvestigationResponse(BaseModel):
    investigation_id: str
    scenario_id: str
    status: str
    message: str
    report_id: Optional[str] = None

class SystemStatusResponse(BaseModel):
    version: str
    python_version: str
    dataset_db_available: bool
    operational_db_available: bool
    dataset_db_readonly: bool
    registered_tools: int
    reporting_available: bool

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
