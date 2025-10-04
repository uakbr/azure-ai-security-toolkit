"""Azure resource graph and management API helpers."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, List

try:
    from azure.identity.aio import DefaultAzureCredential
    from azure.mgmt.resourcegraph.aio import ResourceGraphClient
    from azure.mgmt.resourcegraph.models import QueryRequest
except ImportError:  # pragma: no cover - optional Azure SDK
    DefaultAzureCredential = object  # type: ignore
    ResourceGraphClient = object  # type: ignore
    QueryRequest = object  # type: ignore


@dataclass
class AzureQueryResult:
    """Standardised result from Azure queries."""

    data: List[Dict[str, Any]]
    total_records: int


class AzureClient:
    """Wrapper around Azure SDKs with sane defaults and async support."""

    def __init__(self, subscription_id: str) -> None:
        self.subscription_id = subscription_id
        self._credential = None
        self._resource_graph = None

    async def _ensure_clients(self) -> None:
        if self._credential is not None and self._resource_graph is not None:
            return

        if DefaultAzureCredential is object:
            raise RuntimeError(
                "Azure SDK dependencies missing. Install azure-identity and azure-mgmt-resourcegraph."
            )

        self._credential = DefaultAzureCredential()
        self._resource_graph = ResourceGraphClient(credential=self._credential)

    async def close(self) -> None:
        if self._resource_graph:
            await self._resource_graph.close()
        if self._credential and hasattr(self._credential, "close"):
            await self._credential.close()

    async def query(self, query: str) -> AzureQueryResult:
        """Execute an Azure Resource Graph query."""
        await self._ensure_clients()
        request = QueryRequest(subscriptions=[self.subscription_id], query=query)
        response = await self._resource_graph.resources(request)  # type: ignore[call-arg]
        data = response.data if hasattr(response, "data") else []
        count = len(data) if data else 0
        return AzureQueryResult(data=list(data), total_records=count)

    async def list_azure_ai_resources(self) -> AsyncIterator[Dict[str, Any]]:
        """Yield Azure AI resources relevant to the scanner."""
        queries = {
            "azure_openai": """
                resources
                | where type =~ 'microsoft.cognitiveservices/accounts'
                | project name, id, type, location, properties
            """,
            "ml_workspaces": """
                resources
                | where type =~ 'microsoft.machinelearningservices/workspaces'
                | project name, id, type, location, properties
            """,
            "cognitive_services": """
                resources
                | where type has 'Microsoft.CognitiveServices'
                | project name, id, type, location, properties
            """,
        }

        for resource_type, query in queries.items():
            result = await self.query(query)
            for row in result.data:
                enriched = dict(row)
                enriched["resource_type"] = resource_type
                yield enriched

    async def __aenter__(self) -> "AzureClient":
        await self._ensure_clients()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()


async def gather_with_concurrency(limit: int, *tasks: Any) -> List[Any]:
    """Utility for bounding concurrent async operations."""
    semaphore = asyncio.Semaphore(limit)

    async def sem_task(task: Any) -> Any:
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(t) for t in tasks))
