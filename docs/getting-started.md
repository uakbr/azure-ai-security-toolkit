# Getting Started

This guide walks through setting up the Azure AI Security Toolkit locally and in Azure.

1. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Authenticate with Azure**
   ```bash
   az login
   az account set --subscription <SUBSCRIPTION_ID>
   ```
3. **Run baseline security scan**
   ```bash
   python scanner/cli.py --subscription-id <SUBSCRIPTION_ID>
   ```
4. **Deploy secure MLOps scaffolding**
   ```bash
   terraform -chdir=mlops-templates/terraform init
   terraform -chdir=mlops-templates/terraform apply -var prefix=myai
   ```
5. **Start AI Firewall proxy locally**
   ```bash
   uvicorn ai-firewall.server:app --host 0.0.0.0 --port 8080
   ```

Refer to the `examples/` directory for reference implementations.
