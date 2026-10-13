"""
FastAPI REST API Server for Point Of Care Connectivity Agent.
"""
from pathlib import Path
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel, Field
from .base import AuditLogger, SecurityException
from .metrics import GLOBAL_METRICS
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Point Of Care Connectivity Agent API",
    description="Enterprise Distributed Component Platform (Clinical & Biomedical AI)",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "point-of-care-connectivity-agent", "domain": "Clinical & Biomedical AI", "standard": "CAP / CLSI / ISO Standards", "version": "3.0.0-ENTERPRISE"}


@app.get("/")
def operations_console():
    page = Path(__file__).resolve().parent.parent / "web" / "index.html"
    if not page.is_file():
        page = Path(sys.prefix) / "share" / "point-of-care-connectivity-agent" / "index.html"
    if not page.is_file():
        raise HTTPException(status_code=404, detail="Operations console is unavailable")
    return FileResponse(page, media_type="text/html", headers={"Cache-Control": "no-store"})


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "critical_tasks_total": GLOBAL_METRICS.critical_alerts_total,
        "elevated_tasks_total": GLOBAL_METRICS.elevated_alerts_total,
        "phi_blocks_total": GLOBAL_METRICS.phi_blocks_total,
        "audit_chain_verified": AuditLogger.verify_integrity(),
    }


@app.get("/metrics/prometheus", response_class=PlainTextResponse)
def prometheus_metrics():
    return GLOBAL_METRICS.export_prometheus_text()


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException:
        raise HTTPException(status_code=422, detail="Recognizable personal identifiers are not accepted") from None
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise HTTPException(status_code=422, detail="Recognizable personal identifiers are not accepted") from None


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
