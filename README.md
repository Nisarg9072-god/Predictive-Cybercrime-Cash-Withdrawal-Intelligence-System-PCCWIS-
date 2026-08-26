# Predictive Cybercrime Intelligence Agent

Development of a Predictive Analytics Framework for Cybercrime Complaints to Forecast Likely Cash Withdrawal Locations in Advance, Enabling Generation of Actionable Intelligence for Timely and Proactive Cybercrime Intervention.

## Architecture

This project uses a LangGraph-based AI agent to investigate cybercrimes:
1. Ingest Complaint
2. Fetch Account Details
3. Trace Transaction Graph
4. Assess Account Risk
5. Predict Withdrawal Location
6. Verify Evidence
7. Generate Report

## Setup & Installation

1. Install Python 3.11+
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies: `pip install -e .[dev]` or `pip install -r requirements.txt` if available. (Note: using `pyproject.toml` is recommended, so `pip install -e .` works).

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:
```bash
cp .env.example .env
```

## Running the Agent

To run the CLI demonstration:
```bash
python -m cli.main
```
Enter `CASE-001` when prompted.

## Running Tests

To run the test suite:
```bash
pytest
```

## Documentation
- `docs/CONTRIBUTING.md`: Rules for contributing and Git workflow.
- `docs/DEVELOPER_HANDOFF.md`: Instructions for team members regarding the architecture, shared contracts, and boundaries.
