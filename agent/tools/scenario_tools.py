from typing import Any
from .registry_types import ToolResult
from database.repository import DatasetRepository

def get_scenario(scenario_id: str) -> ToolResult:
    try:
        scenario = DatasetRepository.get_scenario(scenario_id)
        if scenario:
            return ToolResult(success=True, tool_name="get_scenario", data=scenario.model_dump())
        return ToolResult(success=False, tool_name="get_scenario", error={"message": "Not found"})
    except Exception as e:
        return ToolResult(success=False, tool_name="get_scenario", error={"message": str(e)})

def get_scenario_raw(scenario_id: str) -> ToolResult:
    try:
        scenario = DatasetRepository.get_scenario_raw(scenario_id)
        if scenario:
            return ToolResult(success=True, tool_name="get_scenario_raw", data=scenario)
        return ToolResult(success=False, tool_name="get_scenario_raw", error={"message": "Not found"})
    except Exception as e:
        return ToolResult(success=False, tool_name="get_scenario_raw", error={"message": str(e)})
