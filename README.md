# GenBuilder — LLM-Driven Generative Design Parameter Optimizer

GenBuilder is an agentic pipeline where an LLM interprets natural language engineering
constraints (load, material, boundary conditions) and generates structured parameter
sets consumable by generative design solvers — bridging the gap between designer intent
and solver configuration.

## Architecture

```
                         ┌──────────────────────────────────────┐
                         │           GenBuilder API             │
                         │          (FastAPI + Uvicorn)         │
                         └──────────┬───────────────────────────┘
                                    │
                        ┌───────────▼───────────┐
                        │  ?mode=heuristic (default)
                        │    Regex Parser        │
                        │    + Material DB       │
                        │    + NumPy             │
                        └───────────┬────────────┘
                                    │
     ┌──────────────────────────────┼──────────────────────────────┐
     │              OR  ?mode=crewai                               │
     │  ┌───────────────────────┐  ┌───────────────────────────┐  │
     │  │  Agent 1:             │  │  Agent 2:                 │  │
     │  │  Constraint Parser    │─▶│  Parameter Formatter      │  │
     │  │  (PE persona)         │  │  (CAE persona)            │  │
     │  └───────────────────────┘  └───────────────────────────┘  │
     └─────────────────────────────┬───────────────────────────────┘
                                   │
                         ┌─────────▼─────────┐
                         │  Local Storage     │
                         │  ./outputs/*.json  │
                         └───────────────────┘
```

## Tech Stack

| Layer            | Technology                        |
|------------------|-----------------------------------|
| API              | FastAPI, Pydantic, Uvicorn        |
| AI Agents        | CrewAI, LangChain, OpenAI         |
| Math/Compute     | NumPy                             |
| Storage          | Local JSON files (S3-ready)       |
| Containerization | Docker, Docker Compose            |
| Orchestration    | Kubernetes (manifests included)   |

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy env file and configure
cp .env.example .env
# Edit .env → set OPENAI_API_KEY for CrewAI mode (optional)

# 4. Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Run tests
pytest tests/ -v
```

### Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t genbuilder .
docker run -p 8000:8000 -v ./outputs:/app/outputs genbuilder
```

## Processing Modes

GenBuilder supports two backends, selectable via the `?mode=` query parameter:

| Mode         | Query Param        | Requires API Key | Speed   | Description                         |
|--------------|--------------------|-------------------|---------|-------------------------------------|
| **Heuristic** | `?mode=heuristic` (default) | No       | ~10ms   | Regex parser with material lookup   |
| **CrewAI**    | `?mode=crewai`    | Yes (OpenAI)      | ~15-30s | Full multi-agent LLM pipeline       |

### Heuristic Mode (no LLM, instant)
```bash
curl -X POST "http://localhost:8000/api/generate-parameters?mode=heuristic" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Design a lightweight aluminum bracket that can withstand 500N of tensile load. The part is fixed at two bolt holes on the left face and the load is applied on the right edge. Minimum safety factor of 2.0.",
    "project_name": "bracket-v1"
  }'
```

### CrewAI Mode (LLM agents, more accurate)
```bash
curl -X POST "http://localhost:8000/api/generate-parameters?mode=crewai" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Design a titanium aerospace bracket that handles 5kN of compressive load on the top surface. Fixed at two mounting holes. Safety factor of 4.0.",
    "project_name": "aero-bracket",
    "solver_type": "lattice"
  }'
```

## Multi-Agent Pipeline

The CrewAI pipeline consists of two specialized agents running sequentially:

### Agent 1 — Constraint Parser
- **Role:** Senior Structural Constraint Analyst
- **Job:** Reads the user's natural language description and extracts every engineering constraint (materials, loads, BCs, safety factors, mass limits)
- **Backstory:** A licensed PE with 20 years of structural design experience

### Agent 2 — Parameter Formatter
- **Role:** CAE Parameter Formatting Specialist
- **Job:** Takes extracted constraints and produces solver-ready JSON with correct SI units, normalized direction vectors (NumPy), and validated enum values
- **Backstory:** A CAE specialist who builds FEA preprocessing pipelines

The pipeline includes automatic **fallback to heuristic mode** if the LLM is unavailable or returns malformed output.

## API Endpoints

| Method | Path                        | Description                                  |
|--------|-----------------------------|----------------------------------------------|
| POST   | `/api/generate-parameters`  | Generate structured params from natural lang  |
| GET    | `/api/results`              | List all saved generation results             |
| GET    | `/api/results/{request_id}` | Retrieve a specific result by ID              |
| DELETE | `/api/results/{request_id}` | Delete a saved result                         |
| GET    | `/api/health`               | Service health check                         |
| GET    | `/api/materials`            | List all materials in the reference database  |
| GET    | `/docs`                     | Interactive Swagger UI                       |
| GET    | `/redoc`                    | ReDoc API documentation                      |

## Material Database

Built-in reference library with verified mechanical properties:

| Material           | E (GPa) | σ_y (MPa) | ρ (kg/m³) | ν    |
|-------------------|---------|-----------|-----------|------|
| Aluminum 6061-T6  | 68.9    | 276       | 2710      | 0.33 |
| AISI 1045 Steel   | 200     | 530       | 7850      | 0.29 |
| Ti-6Al-4V Grade 5 | 113.8   | 880       | 4430      | 0.34 |
| C11000 Copper     | 117     | 69        | 8960      | 0.34 |
| ABS Plastic       | 2.3     | 43        | 1050      | 0.39 |
| Nylon 6/6         | 2.7     | 70        | 1140      | 0.39 |

## Project Structure

```
genbuilder/
├── app/
│   ├── api/
│   │   └── routes.py             # FastAPI route handlers + results CRUD
│   ├── agents/
│   │   ├── constraint_parser.py  # Agent 1: extracts constraints
│   │   ├── parameter_formatter.py# Agent 2: formats solver JSON
│   │   └── crew.py               # CrewAI orchestrator
│   ├── core/
│   │   └── config.py             # Pydantic-settings configuration
│   ├── models/
│   │   ├── requests.py           # Input schemas (DesignRequest)
│   │   └── responses.py          # Output schemas (DesignParameterSet)
│   └── services/
│       ├── parameter_service.py  # Heuristic parser + material DB
│       └── storage_service.py    # Local JSON file storage
├── aws/                          # Reserved for future cloud integration
├── k8s/
│   ├── deployment.yaml           # K8s deployment (2 replicas)
│   ├── service.yaml              # K8s service (LoadBalancer)
│   └── hpa.yaml                  # Horizontal Pod Autoscaler (2-10 pods)
├── outputs/                      # Generated results (auto-created)
├── tests/
│   └── test_api.py               # 10 integration tests (all passing)
├── Dockerfile                    # Multi-stage, non-root, healthcheck
├── docker-compose.yml            # Local containerized development
├── .env.example
├── requirements.txt
└── README.md
```

## Upgrading to Cloud

The storage layer is designed for easy migration:

1. **AWS S3:** Replace `storage_service.py` with an S3 implementation using `boto3` (same interface: `save/get/list/delete`)
2. **AWS Lambda:** Add a function in `aws/` that triggers on S3 uploads to relay parameters to a solver
3. The `s3_uri` field in the API response will automatically switch from `local://` to `s3://`

## Build Progress

- [x] **Phase 1:** Foundation & FastAPI API (Pydantic models, routes, validation)
- [x] **Phase 2:** CrewAI Multi-Agent System (Constraint Parser + Parameter Formatter)
- [x] **Phase 3:** Local Storage & Results API (save, list, retrieve, delete)
- [x] **Phase 4:** Docker & Kubernetes (Dockerfile, Compose, K8s manifests + HPA)
- [ ] **Optional:** AWS S3 + Lambda integration

## License

MIT
