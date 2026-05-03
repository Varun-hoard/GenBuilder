"""
GenBuilder — API Integration Tests

Validates the FastAPI endpoints with realistic engineering prompts.
Run with:  pytest tests/ -v
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── Health Check ──────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_health_check(client: AsyncClient):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "GenBuilder"


# ── Generate Parameters — Aluminum Bracket ───────────────────────────

@pytest.mark.anyio
async def test_generate_parameters_aluminum(client: AsyncClient):
    payload = {
        "description": (
            "Design a lightweight aluminum bracket that can withstand 500N "
            "of tensile load. The part is fixed at two bolt holes on the "
            "left face and the load is applied on the right edge. "
            "Minimum safety factor of 2.0."
        ),
        "project_name": "bracket-v1",
        "solver_type": "topology_optimization",
    }

    response = await client.post("/api/generate-parameters", json=payload)
    assert response.status_code == 200

    data = response.json()
    params = data["parameters"]

    # Project metadata
    assert params["project_name"] == "bracket-v1"
    assert params["solver_type"] == "topology_optimization"

    # Material — should detect aluminum
    assert len(params["materials"]) >= 1
    assert "aluminum" in params["materials"][0]["name"].lower()
    assert params["materials"][0]["youngs_modulus_pa"] == pytest.approx(68.9e9)

    # Loads — should parse 500N
    assert len(params["loads"]) >= 1
    assert params["loads"][0]["magnitude_n"] == pytest.approx(500.0)

    # Boundary conditions
    assert len(params["boundary_conditions"]) >= 1
    assert params["boundary_conditions"][0]["constraint_type"] == "fixed"

    # Objectives
    assert params["objectives"]["safety_factor"] == pytest.approx(2.0)

    # Response metadata
    assert data["status"] == "completed"
    assert "request_id" in data


# ── Generate Parameters — Steel Plate ────────────────────────────────

@pytest.mark.anyio
async def test_generate_parameters_steel(client: AsyncClient):
    payload = {
        "description": (
            "Design a steel mounting plate for a 1kN vertical load. "
            "The plate is bolted at four corners and the load is applied "
            "at the center. Use AISI 1045 steel. Target mass under 2 kg. "
            "Safety factor of 3.0."
        ),
        "project_name": "mounting-plate-v2",
    }

    response = await client.post("/api/generate-parameters", json=payload)
    assert response.status_code == 200

    data = response.json()
    params = data["parameters"]

    # Material — should detect steel
    assert "steel" in params["materials"][0]["name"].lower()

    # Loads — should parse 1kN = 1000N
    assert params["loads"][0]["magnitude_n"] == pytest.approx(1000.0)

    # Objectives
    assert params["objectives"]["safety_factor"] == pytest.approx(3.0)
    assert params["objectives"]["max_mass_kg"] == pytest.approx(2.0)


# ── Generate Parameters — Titanium (kN unit) ─────────────────────────

@pytest.mark.anyio
async def test_generate_parameters_titanium(client: AsyncClient):
    payload = {
        "description": (
            "I need a titanium aerospace bracket that handles 5kN of "
            "compressive load applied on the top surface. The base is "
            "fixed at two mounting holes. Safety factor of 4.0."
        ),
        "project_name": "aero-bracket",
        "solver_type": "lattice",
    }

    response = await client.post("/api/generate-parameters", json=payload)
    assert response.status_code == 200

    data = response.json()
    params = data["parameters"]

    mat_name = params["materials"][0]["name"].lower()
    assert "ti" in mat_name or "titanium" in mat_name
    assert params["loads"][0]["magnitude_n"] == pytest.approx(5000.0)
    assert params["solver_type"] == "lattice"
    assert params["objectives"]["safety_factor"] == pytest.approx(4.0)


# ── Validation: Description too short ────────────────────────────────

@pytest.mark.anyio
async def test_validation_short_description(client: AsyncClient):
    payload = {
        "description": "too short",
        "project_name": "fail",
    }

    response = await client.post("/api/generate-parameters", json=payload)
    assert response.status_code == 422  # Pydantic validation error


# ── Materials List ───────────────────────────────────────────────────

@pytest.mark.anyio
async def test_list_materials(client: AsyncClient):
    response = await client.get("/api/materials")
    assert response.status_code == 200

    data = response.json()
    assert data["count"] >= 4  # at least aluminum, steel, titanium, copper
    assert "aluminum" in data["materials"]
    assert "steel" in data["materials"]


# ── Root Redirects to Docs ───────────────────────────────────────────

@pytest.mark.anyio
async def test_root_redirect(client: AsyncClient):
    response = await client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert "/docs" in response.headers.get("location", "")


# ── Result Persistence ───────────────────────────────────────────────

@pytest.mark.anyio
async def test_generate_saves_result_locally(client: AsyncClient):
    """Generating parameters should auto-save and return a local path."""
    payload = {
        "description": (
            "Design a copper heat sink for 200N of distributed load. "
            "The base is fixed at four screw holes. Safety factor of 1.5."
        ),
        "project_name": "heatsink-test",
    }

    response = await client.post("/api/generate-parameters", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["s3_uri"] is not None
    assert data["s3_uri"].startswith("local://")

    # Retrieve the result by ID
    request_id = data["request_id"]
    get_resp = await client.get(f"/api/results/{request_id}")
    assert get_resp.status_code == 200

    result = get_resp.json()
    assert result["request_id"] == request_id
    assert result["project_name"] == "heatsink-test"


@pytest.mark.anyio
async def test_list_results(client: AsyncClient):
    """The results listing endpoint should return saved results."""
    response = await client.get("/api/results")
    assert response.status_code == 200

    data = response.json()
    assert "count" in data
    assert "results" in data
    assert isinstance(data["results"], list)


@pytest.mark.anyio
async def test_get_nonexistent_result(client: AsyncClient):
    """Requesting a non-existent result should return 404."""
    response = await client.get("/api/results/does-not-exist-999")
    assert response.status_code == 404

