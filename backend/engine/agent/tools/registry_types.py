from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class ToolResult(BaseModel):
    """
    Shared contract for all tool responses.
    Every tool implementation must return this structure.
    """
    success: bool = Field(description="True if the tool executed successfully, False otherwise.")
    tool_name: str = Field(description="The name of the tool that was executed.")
    data: Optional[Any] = Field(description="The successful output data of the tool.", default=None)
    error: Optional[Dict[str, Any]] = Field(description="Error details if success is False.", default=None)
    metadata: Dict[str, Any] = Field(description="Additional metadata.", default_factory=dict)
