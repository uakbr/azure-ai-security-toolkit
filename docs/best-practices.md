# Security Best Practices

1. **Enforce least privilege** — use managed identities and scoped access policies for all automation identities.
2. **Disable public network access** — require private endpoints for Azure OpenAI, Cognitive Services, and ML workspaces.
3. **Enable encryption with CMK** — configure customer-managed keys backed by Azure Key Vault.
4. **Integrate continuous testing** — run adversarial and prompt injection tests as part of CI/CD.
5. **Monitor telemetry centrally** — stream firewall logs and scanner findings to Azure Sentinel.
6. **Automate remediation** — leverage SOAR playbooks to isolate compromised models and rotate secrets.
7. **Adopt responsible AI** — track fairness metrics, maintain model cards, and document decisions.
8. **Govern AI-assisted coding** — enforce policy-as-code for GitHub Copilot and track usage analytics.
