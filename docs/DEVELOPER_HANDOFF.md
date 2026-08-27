# Developer Handoff & Architecture Guide

Welcome to the Predictive Cybercrime Intelligence Agent repository!
This document outlines the foundation that has been built and the boundaries each developer must respect.

## What is Already Implemented

- **Project Structure**: Logical separation for agent, ml, data, cli, and tests.
- **Base Agent Graph**: A LangGraph setup in `agent/graph/graph.py` containing the core sequence of operations.
- **Shared Contracts**: Strongly typed state and tool responses.
- **Mock CLI**: A basic CLI in `cli/main.py` that runs the agent loop with mock tools.

## Folder Ownership

- **Person 1**: Agent core + repository architecture (`agent/graph/`, root configs)
- **Person 2**: Transaction graph (`agent/tools/transaction_tools.py`, `agent/tools/graph_tools.py`)
- **Person 3**: ML + risk engine (`ml/`, `agent/tools/risk_tools.py`)
- **Person 4**: Tool layer + APIs (`agent/tools/`, excluding ML/Graph specific parts)
- **Person 5**: Evaluation + test scenarios (`evaluation/`, `tests/`)
- **Person 6**: CLI + integration (`cli/`)

Please work **inside** your assigned areas.

## Shared Contracts (DO NOT CHANGE without team approval)

### 1. State Contract (`InvestigationState`)
Located in `agent/graph/state.py`.
This is the single source of truth for the agent's memory. If your component needs to store something for the next node, it MUST go here. Do not invent your own state structures.

### 2. Tool Contract (`ToolResult`)
Located in `agent/tools/registry.py`.
Every tool must return this exact structure:
```python
{
    "success": bool,
    "tool_name": str,
    "data": dict | list | None,
    "error": dict | None,
    "metadata": dict
}
```

## How to Run the Project

```bash
# Install dependencies
pip install -e .[dev]

# Run the CLI
python -m cli.main

# Run tests
pytest
```

## How to Add a New Tool
1. Add your logic in the appropriate file in `agent/tools/`.
2. Ensure it returns a `ToolResult`.
3. Add it to `agent/tools/registry.py` or import it directly into `agent/graph/nodes.py`.

## How to Add a New LangGraph Node
1. Create a function in `agent/graph/nodes.py` that takes `InvestigationState` and returns a dict with the fields to update.
2. Add it to the workflow in `agent/graph/graph.py`.

## How to Report a Breaking Change
If you MUST change `InvestigationState` or `ToolResult`, post in the team channel and wait for a +1 from Person 1 (Architect) before merging.
