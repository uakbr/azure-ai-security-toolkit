"""FastAPI-based security proxy for Azure OpenAI."""
from __future__ import annotations

import os
from typing import Any, Dict

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from .config import FirewallConfig
from .detectors import DataExfiltrationDetector, PromptInjectionDetector
from .middleware import RateLimiter, log_request

app = FastAPI(title="Azure AI Security Proxy", version="0.1.0")

_detector = PromptInjectionDetector()
_exfil_detector = DataExfiltrationDetector()
_rate_limiter = RateLimiter(max_per_minute=60)


async def get_config() -> FirewallConfig:
    try:
        return FirewallConfig(
            azure_openai_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            azure_openai_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            rate_limit_per_minute=int(os.getenv("RATE_LIMIT", "60")),
        )
    except KeyError as exc:  # pragma: no cover - env misconfiguration
        raise RuntimeError(f"Missing configuration: {exc}") from exc


async def _proxy_request(
    request: Request,
    config: FirewallConfig,
    authorization: str | None = Header(default=None),
) -> Dict[str, Any]:
    await log_request(request, {"tenant": "default"})
    payload = await request.json()
    if "messages" not in payload:
        raise HTTPException(status_code=400, detail="Invalid OpenAI payload")

    content = "\n".join(message.get("content", "") for message in payload["messages"])
    detection = await _detector.detect(content)
    if detection.detected:
        raise HTTPException(status_code=403, detail={"reason": detection.reasons})

    exfil = await _exfil_detector.detect(content)
    if exfil.detected:
        raise HTTPException(status_code=403, detail={"reason": exfil.reasons})

    api_headers = {
        "api-key": config.api_key,
        "Content-Type": "application/json",
        "Authorization": authorization or "",
    }

    endpoint = f"{config.azure_openai_endpoint}/openai/deployments/{config.azure_openai_deployment}/chat/completions?api-version=2023-05-15"
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(endpoint, headers=api_headers, json=payload)
        if response.status_code >= 400:
            detail = response.text
            raise HTTPException(status_code=response.status_code, detail=detail)
        return response.json()


@app.post("/v1/chat/completions")
async def chat_completions(
    request: Request,
    config: FirewallConfig = Depends(get_config),
    authorization: str | None = Header(default=None),
) -> JSONResponse:
    client_ip = request.client.host if request.client else "anonymous"
    await _rate_limiter.acquire(client_ip)
    result = await _proxy_request(request, config, authorization)
    return JSONResponse(content=result)


@app.get("/healthz")
async def healthcheck() -> Dict[str, str]:
    return {"status": "ok"}
