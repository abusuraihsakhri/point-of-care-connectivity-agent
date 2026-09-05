# Point Of Care Connectivity Agent

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** CAP / CLSI / ISO Standards

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Point Of Care Connectivity Agent** is an advanced analytical and computational platform implementing Decentralized POCT Glucometer / Blood Gas QC Supervisor. It surveils decentralized glucometers, blood gas carts, and rapid PCR instruments across wards for operator certification, QC lockouts, and calibration.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`Severity`** — Severity evaluation enum with levels: INFO, ADVISORY, WARNING, CRITICAL
- **`DomainKnowledgeRegistry`**: Enterprise domain rules, guideline matrices, and evidence benchmarks
- **`AgentAlert`** — Alert evaluation and state verification module
- **`OperatorCertificationAgent`**: Sub-Agent for operator certification verification
- **`DeviceLockoutMonitorAgent`**: Sub-Agent for device lockout monitoring
- **`InterInstrumentBiasAgent`**: Sub-Agent for inter-instrument bias detection

### 🏗️ Architecture Components

- **`agents/base.py`** — Enterprise Security, PHI Outbound Guard, and HMAC-SHA256 Audit Trail
- **`agents/workers.py`** — Specialized domain worker agents (QC, Safety, Protocol Conformance)
- **`agents/supervisor.py`** — Master supervisor orchestrator
- **`agents/api.py`** — FastAPI REST API server
- **`agents/llm_factory.py`** — LLM provider factory (supports mock, Ollama, Claude, OpenAI)
- **`agents/metrics.py`** — Prometheus operational metrics exporter
- **`agents/learning.py`** — Bayesian calibration and active learning feedback engine

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/point-of-care-connectivity-agent.git
cd point-of-care-connectivity-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn pydantic pytest

# Optional: Set audit secret key for persistent audit integrity
export AUDIT_SECRET_KEY="your-secure-key-here"  # On Windows: set AUDIT_SECRET_KEY=...
```

See `.env.example` for all configuration options.

---

## 💻 CLI Quickstart & Usage

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-2026-001 --target KEY-TARGET-01 --primary 28.5 --secondary 14.2
```

### 2. System Query (Chat)
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
| Argument | Description | Default |
|:---------|:------------|:--------|
| `--task-id` | Unique task/case identifier | TASK-2026-001 |
| `--target` | Target entity or specimen identifier | KEY-TARGET-01 |
| `--primary` | Primary measurement value (float) | 28.5 |
| `--secondary` | Secondary measurement value (float) | 14.2 |
| `--critical` | Flag for critical/emergency escalation | False |
| `--status` | Status descriptor (NOMINAL, DISCORDANT, etc.) | DISCORDANT |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation
* **PHI Redaction:** Automatic redaction of sensitive identifiers in output
* **Audit Secret Key:** Configurable via `AUDIT_SECRET_KEY` environment variable (random key generated if not set)

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t point-of-care-connectivity-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-key point-of-care-connectivity-agent
```

Or using Docker Compose:

```bash
docker-compose up -d
```

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |
| POST | `/api/audit` | Submit task for evaluation |
| POST | `/api/chat` | Query supervisory assistant |
| GET | `/api/audit/logs` | Retrieve and verify audit trail |

---

## 📁 Project Structure

```
point-of-care-connectivity-agent/
├── agents/                 # Core agent modules
│   ├── base.py            # Security, PHI Guard, Audit Trail
│   ├── supervisor.py      # Supervisor orchestrator
│   ├── workers.py         # Specialized worker agents
│   ├── models.py          # Pydantic data models
│   ├── api.py             # FastAPI REST server
│   ├── llm_factory.py     # LLM provider factory
│   ├── metrics.py         # Prometheus metrics
│   ├── learning.py        # Bayesian calibration engine
│   └── streamer.py        # WebSocket telemetry
├── tests/                 # Test suite
├── web/                   # Web operations console
├── cli.py                 # Command-line interface
├── poct_sentinel.py       # Legacy POCT sentinel module
├── enrichment.py          # Enrichment feature engines
├── simulator.py           # High-throughput simulation
├── Dockerfile             # Container build
├── docker-compose.yml     # Container orchestration
├── pyproject.toml         # Project configuration
└── .env.example           # Environment configuration template
```

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
