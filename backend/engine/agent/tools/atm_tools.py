from typing import Any
from .registry_types import ToolResult
from database.repository import DatasetRepository

def get_atm(atm_id: str) -> ToolResult:
    try:
        atm = DatasetRepository.get_atm(atm_id)
        if atm:
            return ToolResult(success=True, tool_name="get_atm", data=atm.model_dump())
        return ToolResult(success=False, tool_name="get_atm", error={"message": "Not found"})
    except Exception as e:
        return ToolResult(success=False, tool_name="get_atm", error={"message": str(e)})
