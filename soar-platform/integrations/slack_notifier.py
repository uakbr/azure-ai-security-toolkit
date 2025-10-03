"""Slack notification helper."""
from __future__ import annotations


class SlackNotifier:
    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    async def send_message(self, message: str) -> None:
        print(f"[Slack] {message}")
