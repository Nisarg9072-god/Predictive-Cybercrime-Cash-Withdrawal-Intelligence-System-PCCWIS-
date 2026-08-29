from typing import Any
from .registry_types import ToolResult
from database.repository import DatasetRepository

def get_profile(identifier: str) -> ToolResult:
    try:
        profile = DatasetRepository.get_profile(identifier)
        if profile:
            return ToolResult(success=True, tool_name="get_profile", data=profile.model_dump())
        return ToolResult(success=False, tool_name="get_profile", error={"message": "Not found"})
    except Exception as e:
        return ToolResult(success=False, tool_name="get_profile", error={"message": str(e)})

def get_mule_profiles() -> ToolResult:
    try:
        profiles = DatasetRepository.get_mule_profiles()
        return ToolResult(success=True, tool_name="get_mule_profiles", data=[p.model_dump() for p in profiles])
    except Exception as e:
        return ToolResult(success=False, tool_name="get_mule_profiles", error={"message": str(e)})
