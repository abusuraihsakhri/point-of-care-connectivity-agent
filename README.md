# Point of Care Connectivity Agent

A local Python prototype for evaluating **synthetic point-of-care testing (POCT) measurements** against example rules, producing alerts and an in-memory HMAC-SHA256 audit chain. It provides a command-line interface, REST API, and browser-based operations console.

**Research/development use only.** The thresholds are illustrative, not validated analyte-specific QC limits. This project does **not** connect to glucometers, blood-gas analyzers, LIS systems, or real operator-certification databases. It is not a clinical decision-support device and must not be used with patient data or for patient care.

## Features

- Evaluate primary values above **25**, secondary values above **12**, explicit critical flags, and discordance descriptors with three example workers.
- Inspect a structured dossier with urgency, integrity status, rule-based alerts, and audit hash.
- Process individual requests or CSV batches; interrogate the local mock chat endpoint.
- Check per-entry HMAC-SHA256 audit signatures and chain links while the process is running.
- Use a responsive local operations console with actual API connectivity, metrics, validation and error states.
- Run automated regression tests for inputs, CSV flags, signing, and API behavior.

The repository also retains alternative historical implementations in `poct_sentinel.py` and `point_of_care_connectivity_agent/`; their rule sets and CLI interfaces are distinct from the primary `agents/` engine.

## Run locally

Requires Python 3.10 or newer.

```bash
git clone https://github.com/abusuraihsakhri/point-of-care-connectivity-agent.git
cd point-of-care-connectivity-agent
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

# Generate a strong key for this session. Set a stable private key for repeated runs.
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"

point-of-care-connectivity-agent serve --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000/** for the operations console, or **http://127.0.0.1:8000/docs** for interactive API documentation. Browser and API requests use the same origin. The console requires a running Python server and cannot operate as a standalone GitHub Pages application.

Windows PowerShell: activate the virtual environment with `.venv\Scripts\Activate.ps1` and set `$env:AUDIT_SECRET_KEY` to a private random key.

### CLI examples

```bash
point-of-care-connectivity-agent audit --task-id SYNTH-001 --target DEVICE-DEMO --primary 28.5 --secondary 14.2
point-of-care-connectivity-agent chat "What is the status?"
point-of-care-connectivity-agent batch -i sample.csv -o results.csv
point-of-care-connectivity-agent verify-audit
```

CSV accepts `task_id`/`case_id`, `target_identifier`/`patient_synthetic_id`, `primary_metric`/`metric_primary`, `secondary_metric`/`metric_secondary`, `is_critical_flag`/`is_stat`, and `status_descriptor`/`status_flag`. Boolean columns accept true/false, yes/no, and 1/0. Output is escaped to reduce spreadsheet formula-injection risk.

The legacy command `point-of-care-connectivity-engine` remains available for the alternative `point_of_care_connectivity_agent` CLI.

## REST API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Operations console |
| GET | `/health` | Server health |
| GET | `/metrics` | JSON activity metrics |
| GET | `/metrics/prometheus` | Prometheus-format counters |
| POST | `/api/audit` | Evaluate a synthetic task |
| POST | `/api/chat` | Local deterministic mock response |
| GET | `/api/audit/logs` | In-memory signed audit entries and integrity check |

For example:

```bash
curl -sS http://127.0.0.1:8000/api/audit \
  -H "Content-Type: application/json" \
  -d '{"task_id":"SYNTH-01","target_identifier":"DEVICE-01","primary_metric":27,"secondary_metric":5,"status_descriptor":"NOMINAL","is_critical_flag":false}'
```

## Security and limitations

- **Synthetic inputs only.** A regex-based identifier guard blocks some recognizable MRNs, SSNs, contact details, and names. This is not complete de-identification or HIPAA compliance.
- The HMAC key is read from `AUDIT_SECRET_KEY`; without it, the process generates a temporary key and emits a warning. Audit records, counters, and dossiers are held **only in memory** and are lost on restart. The audit chain is tamper-evident within the running process, not a durable or externally anchored ledger.
- There is **no API authentication, authorization, TLS termination, or persistent database**. Bind to loopback only unless you add an appropriate secured reverse proxy and authentication. Never expose the API or logs directly on the public internet.
- The chat response is a deterministic mock, not a clinical-language model. No third-party services are required for the operations console.
- The sample thresholds and recommendation texts are development examples; clinical guidelines and instrument interoperability are not implemented or verified.

## Tests and Docker

```bash
python -m pytest -q
python -m compileall -q agents point_of_care_connectivity_agent cli.py poct_sentinel.py enrichment.py
```

Docker Compose reads `AUDIT_SECRET_KEY` from the environment and binds the published port to `127.0.0.1`:

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
```

The Docker image installs the package from `pyproject.toml`. CI runs the Python test suite on supported Python versions.

## Technology and license

Python, Pydantic 2, FastAPI, Uvicorn, standard-library HMAC-SHA256, and plain HTML/CSS/JavaScript. The console works in current desktop and mobile browsers with JavaScript enabled, when served through the local API.

MIT license — see [LICENSE](LICENSE).
