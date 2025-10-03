# Secure MLOps Pipeline Template

This template demonstrates a production-ready MLOps setup incorporating security controls aligned with Azure best practices, OWASP for LLMs, and the NIST AI RMF.

## Features

- Infrastructure-as-Code using Bicep and Terraform
- GitHub Actions workflow with security gates (linting, SAST, secrets scanning)
- Model validation pipeline covering bias, robustness, and vulnerability checks
- Azure Key Vault-backed secret management
- Secure model registry operations with scoped access policies
- Runtime monitoring bootstrap for Azure Monitor and Sentinel integration

## Usage

1. Provision infrastructure via Terraform or Bicep modules.
2. Configure GitHub repository secrets for Azure login and Key Vault references.
3. Commit GitHub Actions workflow to enforce security gates.
4. Extend the `scripts/` folder with organisation-specific validation and attestation logic.

Refer to the [docs/getting-started.md](../docs/getting-started.md) guide for a full walkthrough.
