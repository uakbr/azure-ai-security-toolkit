import asyncio
from pathlib import Path

import pytest

from scanner.config import ScannerConfig
from scanner.scanner import AISecurityScanner
from scanner.rules import Rule


@pytest.fixture
def config(tmp_path: Path) -> ScannerConfig:
    return ScannerConfig(subscription_id="00000000-0000-0000-0000-000000000000", output_dir=tmp_path)


@pytest.mark.asyncio
async def test_scanner_detects_public_access(monkeypatch, config: ScannerConfig) -> None:
    resource = {
        "id": "/subscriptions/.../providers/Microsoft.CognitiveServices/accounts/demo",
        "name": "demo",
        "resource_type": "azure_openai",
        "properties": {"publicNetworkAccess": "Enabled"},
    }

    class DummyClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def list_azure_ai_resources(self):
            yield resource

    monkeypatch.setattr("scanner.scanner.AzureClient", DummyClient)

    scanner = AISecurityScanner(config)
    results = await scanner.scan()
    assert results["summary"]["total_findings"] == 1
    assert results["findings"][0]["rule_id"] == "OPENAI-001"


@pytest.mark.asyncio
async def test_custom_rule_injection(config: ScannerConfig) -> None:
    async def evaluator(resource):
        return {"message": "Test"}

    rule = Rule(
        rule_id="CUSTOM-001",
        title="Always fails",
        description="",
        severity="LOW",
        resource_types=["azure_openai"],
        evaluator=evaluator,
        remediation="",
        compliance={},
    )

    class DummyClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def list_azure_ai_resources(self):
            yield {"resource_type": "azure_openai", "id": "1", "name": "demo"}

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr("scanner.scanner.AzureClient", DummyClient)

    scanner = AISecurityScanner(config, extra_rules=[rule])
    results = await scanner.scan()
    assert any(finding["rule_id"] == "CUSTOM-001" for finding in results["findings"])

    monkeypatch.undo()
