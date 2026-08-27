from typing import Any, List
from .registry_types import ToolResult
from database.repository import DatasetRepository

def get_transaction(txn_id: str) -> ToolResult:
    try:
        txn = DatasetRepository.get_transaction(txn_id)
        if txn:
            return ToolResult(success=True, tool_name="get_transaction", data=txn.model_dump())
        return ToolResult(success=False, tool_name="get_transaction", error={"message": "Not found"})
    except Exception as e:
        return ToolResult(success=False, tool_name="get_transaction", error={"message": str(e)})

def get_transaction_chain(chain_id: str) -> ToolResult:
    try:
        txns = DatasetRepository.get_transaction_chain(chain_id)
        return ToolResult(success=True, tool_name="get_transaction_chain", data=[t.model_dump() for t in txns])
    except Exception as e:
        return ToolResult(success=False, tool_name="get_transaction_chain", error={"message": str(e)})

def search_transactions(from_account: str = None, to_account: str = None) -> ToolResult:
    try:
        txns = DatasetRepository.search_transactions(from_account, to_account)
        return ToolResult(success=True, tool_name="search_transactions", data=[t.model_dump() for t in txns])
    except Exception as e:
        return ToolResult(success=False, tool_name="search_transactions", error={"message": str(e)})
