# Evaluation Metrics

The system includes a deterministic evaluation engine designed to grade the quality and completeness of an investigation without relying on subjective LLM evaluations.

These scores are **PROJECT EVALUATION METRICS** and do NOT represent statistical real-world model accuracy unless validated against a tagged ground-truth dataset.

## Metric Breakdown
- **Evidence Quality (0-100)**: Percentage of evidence items with valid classifications and confidence > 0.0.
- **Evidence Completeness (0 or 100)**: Evaluates whether any evidence was successfully collected at all.
- **Finding Consistency (0-100)**: Percentage of generated findings that have valid traced `evidence_ids`.
- **Risk Consistency (0-100)**: Asserts that all computed risk scores are logically within the 0-100 bound.
- **Provenance Score (0-100)**: Measures strict traceability. It calculates the percentage of `DERIVED`, `INFERRED`, or `PREDICTED` evidence items that contain a valid `parent_evidence_id` pointing back to a root `OBSERVED` record.
- **Efficiency Score (0-100)**: Penalizes the agent for exceeding optimal tool-call limits (>20 tool calls).

## Usage
Run the evaluation command via the CLI to grade a completed investigation:
```bash
python -m cli.main evaluate investigation <INVESTIGATION_ID>
```
