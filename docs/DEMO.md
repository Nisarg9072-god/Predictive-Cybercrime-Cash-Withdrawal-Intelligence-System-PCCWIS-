# Synthetic Demonstration Pipeline

Because the 12GB master database dataset contains a known corrupted B-tree index (`idx_atms_geo`), full real-world investigations on specific scenarios will naturally result in a `BLOCKED` status to prevent corrupted or fabricated findings.

To properly demonstrate the end-to-end functionality of the system, a deterministic Synthetic Demonstration mode is available.

## Running the Demo
```bash
python -m cli.main demo run
```

## What the Demo Does
1. **Agent Initialization**: Starts a dummy `SYNTHETIC_DEMO` context.
2. **Observation & Planning**: Mocks the output of the observe and plan nodes.
3. **Execution**: Uses mock data instead of real database tool execution.
4. **Evidence Collection**: Submits structured mock evidence with proper cryptographic hashing.
5. **Risk Engine**: Generates a deterministic risk score based on the mock evidence.
6. **Report Generation**: Builds the comprehensive 18-section PDF report with the highly visible `SYNTHETIC DEMONSTRATION — NOT REAL DATA` watermark.
7. **Verification**: Cryptographically signs the PDF and prints the SHA-256 output.

## Why is this necessary?
The system explicitly forbids the agent from bypassing database corruption or inventing findings. Therefore, to showcase the `PDFGenerator` and `ReportHasher` layers, we must explicitly generate a test investigation where the data is explicitly marked as SYNTHETIC.
