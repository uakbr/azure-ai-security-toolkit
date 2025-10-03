# Architecture Overview

The Azure AI Security Toolkit is organised into modular components that map to the AI security lifecycle.

## Core Services

- **Security Scanner** — Asynchronous scanner that queries Azure Resource Graph and applies security rules. Outputs JSON and Markdown reports.
- **AI Firewall** — FastAPI proxy that inspects chat completions traffic, applies prompt injection detectors, and proxies to Azure OpenAI.
- **Secure MLOps Templates** — Infrastructure-as-Code plus CI/CD workflows to embed security into model lifecycle.
- **Red Team Lab** — Jupyter notebooks for simulated attacks and defensive techniques.
- **Governance Suite** — Responsible AI automation including fairness checks, model cards, and policy enforcement.
- **Copilot Controls** — Policy-as-code and analytics for GitHub Copilot governance.
- **SOAR Platform** — Security orchestration workflows for AI-specific incidents.
- **Continuous Red Teaming** — Automated adversarial testing with scheduled scans.
- **Training Lab** — Interactive challenges for practitioner enablement.
- **Dashboard** — Streamlit application offering real-time security telemetry.

## Data Flow

1. Azure resource inventory is collected via `AzureClient`.
2. Rules engine evaluates configuration and generates findings.
3. Findings are forwarded to governance, SOAR, and dashboard modules.
4. AI Firewall streams telemetry to Azure Monitor & Sentinel via exporters.
5. Automation workflows enforce remediation and update compliance reports.

## Deployment Targets

- Azure Functions for AI Firewall
- Azure Container Apps for streaming analytics
- Azure Machine Learning for secure model deployment
- GitHub Actions for CI/CD automation

Each module is scoped to be deployable independently or as part of the full platform.
