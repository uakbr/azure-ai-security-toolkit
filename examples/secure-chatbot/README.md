# Secure Chatbot Example

End-to-end walkthrough connecting the AI Firewall, security scanner, and governance modules to protect an Azure OpenAI-powered chatbot.

## Steps

1. Deploy infrastructure using `iac/bicep/ai-firewall.bicep`.
2. Configure Azure OpenAI deployment and set environment variables for the firewall.
3. Run the scanner to validate Azure resource posture.
4. Execute red team notebooks: `prompt_injection_basic.ipynb` and `prompt_leakage.ipynb`.
5. Observe blocked requests in the Streamlit dashboard.
6. Review generated model card and fairness reports for compliance evidence.
