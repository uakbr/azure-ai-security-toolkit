"""Middleware helpers for rate limiting and logging."""
from __future__ import annotations

import asyncio
import time
from typing import Dict

from fastapi import HTTPException, Request


class RateLimiter:
    """Very small in-memory token bucket suitable for demo usage."""

    def __init__(self, max_per_minute: int) -> None:
        self.max_per_minute = max_per_minute
        self._tokens: Dict[str, int] = {}
        self._timestamps: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def acquire(self, key: str) -> None:
        async with self._lock:
            now = time.time()
            tokens = self._tokens.get(key, self.max_per_minute)
            last = self._timestamps.get(key, now)
            elapsed = now - last
            refill = int(elapsed / 60 * self.max_per_minute)
            tokens = min(self.max_per_minute, tokens + refill)
            if tokens <= 0:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            self._tokens[key] = tokens - 1
            self._timestamps[key] = now


async def log_request(request: Request, metadata: dict[str, str]) -> None:
    body = await request.json()
    print("[AI-FIREWALL]", request.method, request.url.path, metadata)
    print("Body preview:", str(body)[:200])
