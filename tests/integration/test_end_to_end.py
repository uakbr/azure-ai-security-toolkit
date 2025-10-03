import asyncio
from pathlib import Path

import pytest

from scanner.config import ScannerConfig
from scanner.scanner import AISecurityScanner


@pytest.mark.asyncio
async def test_full_scan_workflow(tmp_path: Path, monkeypatch) -> None:
    config = ScannerConfig(subscription_id="sub", output_dir=tmp_path)

    class DummyClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def list_azure_ai_resources(self):
            yield {
                "id": "1",
                "name": "demo",
                "resource_type": "azure_openai",
                "properties": {"publicNetworkAccess": "Enabled"},
            }

    monkeypatch.setattr("scanner.scanner.AzureClient", DummyClient)

    scanner = AISecurityScanner(config)
    results = await scanner.scan()

    assert "summary" in results
    assert Path(results["report_json"]).exists()
    assert Path(results["report_markdown"]).exists()
