from agent.tools.registry import ToolResult, get_complaint

def test_toolresult_success():
    result = ToolResult(success=True, tool_name="test", data={"key": "value"})
    assert result.success is True
    assert result.data["key"] == "value"

def test_toolresult_failure():
    result = ToolResult(success=False, tool_name="test", error={"message": "failed"})
    assert result.success is False
    assert result.error["message"] == "failed"

def test_mock_get_complaint():
    res = get_complaint("CASE-001")
    assert res.success is True
    assert res.data["case_id"] == "CASE-001"
