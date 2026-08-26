from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field

class ToolResult(BaseModel):
    """
    Shared contract for all tool responses.
    Every tool implementation must return this structure.
    """
    success: bool = Field(description="True if the tool executed successfully, False otherwise.")
    tool_name: str = Field(description="The name of the tool that was executed.")
    data: Optional[Any] = Field(description="The successful output data of the tool.", default=None)
    error: Optional[Dict[str, Any]] = Field(description="Error details if success is False (e.g., {'code': '...', 'message': '...'}).", default=None)
    metadata: Dict[str, Any] = Field(description="Additional metadata (e.g., execution time, source systems).", default_factory=dict)

# ---------------------------------------------------------
# MOCK TOOLS FOR INITIAL AGENT DEVELOPMENT
# ---------------------------------------------------------

def get_complaint(case_id: str) -> ToolResult:
    if case_id == "CASE-001":
        return ToolResult(
            success=True,
            tool_name="get_complaint",
            data={
                "case_id": "CASE-001",
                "victim_account": "V001",
                "amount": 80000,
                "timestamp": "2023-10-25T14:30:00Z",
                "location": "Ahmedabad"
            }
        )
    return ToolResult(
        success=False,
        tool_name="get_complaint",
        error={"code": "NOT_FOUND", "message": f"Case {case_id} not found."}
    )

def get_account_transactions(account_id: str) -> ToolResult:
    # Mock data for demonstration
    transactions = []
    if account_id == "V001":
        transactions.append({"from": "V001", "to": "A101", "amount": 80000, "timestamp": "2023-10-25T14:35:00Z"})
    return ToolResult(
        success=True,
        tool_name="get_account_transactions",
        data={"transactions": transactions}
    )

def trace_transaction_graph(start_account: str, depth: int = 3) -> ToolResult:
    # Synthetic transaction path: V001 -> A101 -> B202 -> ATM-A17
    if start_account == "V001" or start_account == "A101":
        return ToolResult(
            success=True,
            tool_name="trace_transaction_graph",
            data={
                "paths": [
                    {"path": ["V001", "A101", "B202", "ATM-A17"], "amounts": [80000, 80000, 80000]}
                ]
            }
        )
    return ToolResult(success=True, tool_name="trace_transaction_graph", data={"paths": []})

def calculate_account_risk(account_id: str) -> ToolResult:
    risk_score = 0.1
    if account_id == "B202":
        risk_score = 0.92
    return ToolResult(
        success=True,
        tool_name="calculate_account_risk",
        data={"account_id": account_id, "risk_score": risk_score}
    )

def predict_withdrawal_location() -> ToolResult:
    return ToolResult(
        success=True,
        tool_name="predict_withdrawal_location",
        data={
            "predictions": [
                {"location_id": "ATM-A17", "probability": 0.91, "city": "Ahmedabad"}
            ]
        }
    )

def verify_evidence(evidence: List[Any]) -> ToolResult:
    return ToolResult(
        success=True,
        tool_name="verify_evidence",
        data={"verified": True, "notes": "Evidence corroborates a mule account network."}
    )

def generate_report(case_id: str, findings: Any) -> ToolResult:
    return ToolResult(
        success=True,
        tool_name="generate_report",
        data={"report_id": f"REP-{case_id}", "status": "Generated"}
    )
