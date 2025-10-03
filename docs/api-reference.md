# API Reference

## Scanner

### `AISecurityScanner`
- `__init__(config, extra_rules=None)` — Create scanner instance.
- `scan()` — Asynchronously scan subscription and return findings summary.

### CLI Options
- `--subscription-id` — Azure subscription GUID (required).
- `--output-dir` — Directory for reports (default `reports/`).
- `--ruleset` — Additional YAML rules (repeatable).
- `--severity-threshold` — Filter findings by severity level.
- `--tag-filter` — Restrict scanning to resources matching tag.

## AI Firewall

### `POST /v1/chat/completions`
Proxies requests to Azure OpenAI with security checks.

- Headers: `Authorization` (optional Bearer token)
- Body: Standard Azure OpenAI chat payload
- Responses: 200 success; 403 when prompt injection or data exfiltration detected

### `GET /healthz`
Health probe endpoint returning `{ "status": "ok" }`.

## Governance CLI

### `policy_check.py`
- `--config` — Path to YAML policy definitions.
- `--context` — JSON context file describing current state.

Raises non-zero exit on policy violations.

## Copilot Controls

OPA module `copilot.policy` exposes two top-level rules:
- `deny` — Set of reasons for blocking suggestions.
- `require_issue_reference` — Additional guard requiring traceable issues.
