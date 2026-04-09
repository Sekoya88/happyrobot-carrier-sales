from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "dashboard" / "index.html"


def test_dashboard_html_contains_required_hooks():
    html = INDEX.read_text(encoding="utf-8")
    for needle in (
        'id="kpiGrid"',
        'id="outcomeChart"',
        'id="sentimentChart"',
        'id="timelineChart"',
        'id="callsTable"',
        'id="refreshBtn"',
        'id="searchInput"',
        "fetch('/metrics'",
        "x-api-key",
        "loadMetrics",
    ):
        assert needle in html, f"missing: {needle}"


def test_dashboard_js_avoids_innerhtml_for_user_rows():
    """Table rows must stay DOM-safe (textContent / createElement)."""
    html = INDEX.read_text(encoding="utf-8")
    script_start = html.find("<script>")
    script_end = html.rfind("</script>")
    assert script_start != -1 and script_end != -1
    script = html[script_start:script_end]
    assert "innerHTML" not in script
