# Architecture

The Predictive Cybercrime Cash Withdrawal Intelligence System uses a multi-agent orchestrated workflow built on LangGraph to investigate and predict fraudulent cash withdrawal patterns.

## 1. Core Workflow
1. **Agent Initialization**: The system starts an investigation based on a Scenario ID.
2. **Observation (`observe_node`)**: Queries the environment and database to synthesize the current context and evidence.
3. **Hypothesize (`hypothesis_node`)**: Generates investigation vectors based on collected evidence.
4. **Plan (`planner_node`)**: Selects the appropriate deterministic tool based on current hypotheses and available information.
5. **Execute (`tool_execution_node`)**: Invokes database tools against a read-only 12GB SQLite dataset.
6. **Evaluate (`evaluate_node`)**: Processes tool outputs into structured `EvidenceItem` models.
7. **Risk Engine**: Scores the evidence to generate `FindingModel` instances and deterministic risk scores.

## 2. Database Architecture
- **Master Dataset (`cyber_intercept.db`)**: 12GB read-only SQLite database. It is accessed strictly in read-only mode to prevent any modification to raw forensic evidence. It includes a known corrupted index (`idx_atms_geo`), which the system explicitly handles via graceful failure (`BLOCKED` status).
- **Operational Database (`agent.db`)**: A writable SQLite database used to track the agent's internal state, investigations, hypotheses, decisions, evidence, findings, and risk assessments.

## 3. Reporting Pipeline
Generated reports follow a strict cryptographic-hash pipeline. Reports are generated in PDF format, heavily structured into 18 standardized sections, and a SHA-256 hash is generated to verify forensic integrity. Reports can be generated in `REAL` or `SYNTHETIC_DEMO` modes to delineate test data from actual forensic investigations.

## 4. API & CLI Layers
- **CLI**: The command-line interface provides extensive debugging and orchestration commands (`investigate`, `report`, `evaluate`, `demo run`, `system status`).
- **API**: A FastAPI-based REST API allows for external triggering and status checks of background investigations.
