"""Streamlit dashboard for AI security telemetry."""
from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st


class MockDataSource:
    def get_current_security_score(self) -> int:
        return 88

    def get_previous_score(self) -> int:
        return 82

    def get_events_last_24h(self) -> list[dict[str, object]]:
        now = datetime.utcnow()
        return [
            {"timestamp": now - timedelta(hours=i * 3), "type": "PromptInjection", "severity_score": 70 + i * 5}
            for i in range(6)
        ]

    def get_attack_geolocations(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "longitude": [-74.0060, -0.1276, 139.6503],
                "latitude": [40.7128, 51.5072, 35.6762],
                "location": ["New York", "London", "Tokyo"],
                "attack_count": [25, 17, 9],
                "severity": [80, 60, 40],
            }
        )

    def get_recent_alerts(self, limit: int = 5) -> list[dict[str, str]]:
        return [
            {"id": f"ALERT-{i}", "severity": "HIGH", "title": f"Prompt Injection Attempt {i}", "timestamp": datetime.utcnow().isoformat(), "type": "PromptInjection", "description": "Blocked malicious request."}
            for i in range(limit)
        ]


def render_dashboard() -> None:
    st.set_page_config(page_title="Azure AI Security Dashboard", layout="wide")
    st.title("Azure AI Security Platform")

    data_source = MockDataSource()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Security Score", f"{data_source.get_current_security_score()}/100", delta=data_source.get_current_security_score() - data_source.get_previous_score())
    with col2:
        st.metric("Active Threats", 5)
    with col3:
        st.metric("Blocked Attacks (24h)", 42)

    col1, col2 = st.columns([2, 1])
    with col1:
        events = pd.DataFrame(data_source.get_events_last_24h())
        fig = px.line(events, x="timestamp", y="severity_score", color="type", title="Threat Activity")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        geo = data_source.get_attack_geolocations()
        map_fig = px.scatter_geo(geo, lat="latitude", lon="longitude", size="attack_count", color="severity", hover_name="location", projection="natural earth")
        st.plotly_chart(map_fig, use_container_width=True)

    st.subheader("Recent Alerts")
    for alert in data_source.get_recent_alerts():
        st.write(f"**{alert['title']}** — {alert['description']}")


if __name__ == "__main__":
    render_dashboard()
