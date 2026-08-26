# Contributing Guidelines

## Git Workflow

We use a feature branch workflow.
`main` -> Production / Stable
`develop` -> Active development branch

All feature branches MUST originate from `develop`.

### Recommended Branches
- `feature/agent-core`
- `feature/transaction-graph`
- `feature/ml-risk`
- `feature/tool-layer`
- `feature/evaluation`
- `feature/cli-integration`

## Rules
- **NEVER** force push to shared branches (`main`, `develop`).
- **NEVER** rewrite shared branch history.
- **NO DIRECT COMMITS** to `develop` or `main`. Use Pull Requests.
- **NO BREAKING CHANGES** to shared contracts (`InvestigationState`, `ToolResult`) without team approval.

## Pull Requests
- PRs should be reviewed by at least one other team member.
- Ensure all tests pass before merging.
- Title format: `[Domain] Description of change` (e.g., `[ML] Add risk scoring model`).

## Testing Requirement
Any new feature MUST include basic unit tests. Do not merge untested logic that breaks the agent loop.
