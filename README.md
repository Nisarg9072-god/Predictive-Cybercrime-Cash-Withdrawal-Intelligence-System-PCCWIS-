# Predictive Cybercrime Intelligence Agent

A Predictive Analytics Framework for Cybercrime Complaints to Forecast Likely Cash Withdrawal Locations in Advance, Enabling Generation of Actionable Intelligence for Timely and Proactive Cybercrime Intervention.

## Project Purpose
This system autonomously investigates cybercrime scenarios involving complex money laundering rings and cashout networks. Using an orchestrated agent, it queries a 12GB read-only SQLite database to trace transaction hops, assess profile risk, and generate a standardized, cryptographically hashed PDF assessment report.

## Architecture & System Diagram
The system relies on a LangGraph state machine orchestrating various tools that interact with databases and processing engines.
For an in-depth view of the architecture and database layout, see: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Security Controls
The system implements strict safeguards against false-positive hallucination and database tampering. 
For security models, read-only DB handling, and data provenance, see: [docs/SECURITY.md](docs/SECURITY.md)

## Evaluation Engine
The project features a deterministic grading algorithm that evaluates investigation efficiency, completeness, finding consistency, and provenance strictness.
For evaluation metric definitions, see: [docs/EVALUATION.md](docs/EVALUATION.md)

## CLI Commands

The system features a comprehensive CLI:

**1. System Info**
```bash
python -m cli.main system status
```

**2. Database Inspection**
```bash
python -m cli.main db health
python -m cli.main db schema
```

**3. Run Investigation**
```bash
python -m cli.main investigate scenario <SCENARIO_ID> --verbose
```

**4. Run Report Generation**
```bash
python -m cli.main report investigation <INVESTIGATION_ID>
```

**5. Verify Report Integrity**
```bash
python -m cli.main report verify <REPORT_ID>
```

**6. Evaluate Investigation**
```bash
python -m cli.main evaluate investigation <INVESTIGATION_ID>
```

## API

The system offers a basic, development-only FastAPI layer without authentication. 
To run the API locally:
```bash
uvicorn api.main:app --reload
```
Endpoints include:
- `GET /health`
- `GET /system/status`
- `POST /investigations`
- `GET /investigations/{id}`
- `GET /investigations/{id}/findings`
- `GET /investigations/{id}/evidence`
- `GET /investigations/{id}/report`

## Configuration
Copy `.env.example` to `.env` and fill in the values:
```bash
cp .env.example .env
```
Key limits to configure: `MAX_ITERATIONS` and `MAX_TOOL_CALLS`.

## Installation
1. Install Python 3.11+
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies: `pip install -e .[dev]`

## Running Tests
Run the test suite spanning all phases using:
```bash
pytest -q
```

## Synthetic Demo vs Real-Data Limitations

**IMPORTANT: Database Corruption Limitation**
The master 12GB dataset contains a known corrupted SQLite B-tree index (`idx_atms_geo`). Attempting to trace ATM geolocation and advanced profiling on real scenarios directly triggers database errors. The system is programmed to elegantly catch these errors and produce a `BLOCKED` status rather than returning hallucinated data.

**Synthetic Demo**
Because of the corruption limitation, a full end-to-end trace must be demonstrated using synthetic deterministic data.
See [docs/DEMO.md](docs/DEMO.md) for details. Run the demo via:
```bash
python -m cli.main demo run
```

## Future Work
- Repair or replace the corrupted 12GB dataset index.
- Migrate to a scalable database engine (e.g., PostgreSQL).
- Enable the actual LLM provider module (currently disabled for offline determinism).
- Add robust OAuth2 API Authentication.
