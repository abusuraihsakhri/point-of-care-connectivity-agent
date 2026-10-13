"""Regression tests for security, input validation, API and CSV workflows."""
import csv

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from agents.api import app
from cli import main, parse_csv_bool, safe_csv_cell


def test_audit_signatures_detect_tampering_and_snapshots_are_safe():
    trail = AuditTrail(secret_key="local-test-secret")
    trail.log("supervisor", "test", "EVALUATED", {"ok": True})
    trail.log("supervisor", "test", "EVALUATED", {"ok": False})
    assert trail.verify_integrity()

    snapshot = trail.get_trail()
    snapshot[0]["event_type"] = "changed"
    assert trail.verify_integrity()
    assert trail.get_trail()[0]["event_type"] == "EVALUATED"

    trail.logs[0]["event_type"] = "changed"
    assert not trail.verify_integrity()


def test_payload_rejects_nonfinite_and_extra_inputs():
    valid = dict(task_id="SYNTH-1", target_identifier="KEY-1", primary_metric=2.0)
    with pytest.raises(ValidationError):
        SystemTaskPayload(**{**valid, "primary_metric": float("nan")})
    with pytest.raises(ValidationError):
        SystemTaskPayload(**{**valid, "primary_metric": float("inf")})
    with pytest.raises(ValidationError):
        SystemTaskPayload(**{**valid, "unexpected_field": "ignored"})
    with pytest.raises(ValidationError):
        SystemTaskPayload(**{**valid, "task_id": ""})


def test_nested_identifier_guard_rejects_metadata():
    supervisor = SystemSupervisor()
    payload = SystemTaskPayload(
        task_id="SYNTH-1", target_identifier="KEY-1", primary_metric=1,
        attributes={"notes": {"email": "test@example.com"}},
    )
    with pytest.raises(SecurityException):
        supervisor.process_task(payload)


@pytest.mark.parametrize("raw,expected", [
    ("True", True), ("False", False), ("0", False), ("1", True),
    ("yes", True), ("no", False), ("", False),
])
def test_csv_flags(raw, expected):
    assert parse_csv_bool(raw) is expected


def test_csv_invalid_flag_rejected():
    with pytest.raises(ValueError):
        parse_csv_bool("maybe")


def test_csv_batch_supports_sample_headers_and_false_string(tmp_path):
    src = tmp_path / "in.csv"
    dst = tmp_path / "out.csv"
    src.write_text(
        "case_id,patient_synthetic_id,metric_primary,metric_secondary,is_stat,status_flag\n"
        "SYNTH-1,KEY-1,10,4,False,NOMINAL\n"
        "SYNTH-2,KEY-2,10,4,True,NOMINAL\n",
        encoding="utf-8",
    )
    assert main(["batch", "-i", str(src), "-o", str(dst)]) == 0
    with dst.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert rows[0]["overall_urgency"] == "ROUTINE"
    assert rows[1]["overall_urgency"] == "CRITICAL_STAT_PANIC"


def test_csv_export_escapes_formulas():
    assert safe_csv_cell("  =1+1").startswith("'")
    assert safe_csv_cell("@SUM(A1)").startswith("'")
    assert safe_csv_cell("ordinary") == "ordinary"


def test_api_health_console_validation_and_metrics():
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    console = client.get("/")
    assert console.status_code == 200
    assert "api/audit" in console.text
    start = client.get("/metrics").json()
    assert client.get("/metrics/prometheus").status_code == 200

    ok = client.post("/api/audit", json={
        "task_id": "SYNTH-API-1",
        "target_identifier": "KEY-API-1",
        "primary_metric": 27.0,
        "secondary_metric": 4.0,
        "is_critical_flag": False,
        "status_descriptor": "NOMINAL",
    })
    assert ok.status_code == 200, ok.text
    assert ok.json()["overall_urgency"] == "ELEVATED_RISK"
    later = client.get("/metrics").json()
    assert later["dossiers_processed_total"] == start["dossiers_processed_total"] + 1
    assert later["audit_blocks_total"] == start["audit_blocks_total"] + 1
    assert later["audit_chain_verified"] is True

    rejected = client.post("/api/audit", json={
        "task_id": "SYNTH-API-2",
        "target_identifier": "KEY-API-2",
        "primary_metric": 1,
        "attributes": {"contact": "test@example.com"},
    })
    assert rejected.status_code == 422
    assert client.post("/api/chat", json={"query": "test@example.com"}).status_code == 422

def test_unimplemented_provider_is_not_silently_mocked():
    from agents.llm_factory import LLMFactory
    with pytest.raises(ValueError, match="not implemented"):
        LLMFactory.create("openai")
    with pytest.raises(ValueError, match="not implemented"):
        LLMFactory.create("ollama")


def test_legacy_string_false_is_not_an_emergency():
    from poct_sentinel import DeviceLockoutMonitorAgent
    agent = DeviceLockoutMonitorAgent()
    assert agent.evaluate({"metric_secondary": 2.0, "critical_flag": "False"}) == []
