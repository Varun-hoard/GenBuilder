"""
GenBuilder — API Routes

Defines all HTTP endpoints for the GenBuilder service.
Supports two processing modes:
  - "heuristic" (default) — fast regex-based parser, no LLM needed
  - "crewai" — full multi-agent LLM pipeline via CrewAI

All generated results are automatically saved to a local output directory
and can be retrieved/listed/deleted via the /api/results endpoints.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from enum import Enum

from fastapi import APIRouter, HTTPException, Query, status

from app.models.requests import DesignRequest
from app.models.responses import DesignResponse
from app.services.storage_service import (
    delete_result,
    get_result,
    list_results,
    save_result,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Design Parameters"])


class ProcessingMode(str, Enum):
    """Backend processing engine selection."""
    HEURISTIC = "heuristic"
    CREWAI = "crewai"


# ── Health Check ──────────────────────────────────────────────────────

@router.get(
    "/health",
    summary="Service health check",
    response_model=dict,
)
async def health_check():
    """Return service health status and uptime metadata."""
    return {
        "status": "healthy",
        "service": "GenBuilder",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ── Core Endpoint ────────────────────────────────────────────────────

@router.post(
    "/generate-parameters",
    response_model=DesignResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate structured design parameters from natural language",
    description=(
        "Accepts a natural language description of engineering constraints "
        "(loads, materials, boundary conditions, safety factors) and returns "
        "a structured parameter set consumable by generative design solvers.\n\n"
        "**Modes:**\n"
        "- `heuristic` — fast regex parser, no API key needed\n"
        "- `crewai` — full LLM multi-agent pipeline (requires OPENAI_API_KEY)\n\n"
        "Results are automatically saved locally and can be retrieved via "
        "`GET /api/results/{request_id}`."
    ),
)
async def generate_design_parameters(
    request: DesignRequest,
    mode: ProcessingMode = Query(
        default=ProcessingMode.HEURISTIC,
        description="Processing engine: 'heuristic' (fast, no LLM) or 'crewai' (LLM agents).",
    ),
) -> DesignResponse:
    """
    Main generation endpoint.

    1. Receives plain-English constraints.
    2. Routes to either the heuristic parser or the CrewAI agent pipeline.
    3. Saves the result locally.
    4. Returns a solver-ready JSON payload.
    """
    try:
        logger.info(
            "Generating parameters for project '%s' | solver=%s | mode=%s | input_len=%d",
            request.project_name,
            request.solver_type,
            mode.value,
            len(request.description),
        )

        if mode == ProcessingMode.CREWAI:
            from app.agents.crew import run_design_crew

            parameter_set = run_design_crew(
                description=request.description,
                project_name=request.project_name,
                solver_type=request.solver_type,
            )
        else:
            from app.services.parameter_service import generate_parameters

            parameter_set = generate_parameters(
                description=request.description,
                project_name=request.project_name,
                solver_type=request.solver_type,
            )

        response = DesignResponse(parameters=parameter_set)

        # Save result locally
        local_path = save_result(
            request_id=response.request_id,
            project_name=request.project_name,
            data=parameter_set.model_dump(),
        )
        response.s3_uri = f"local://{local_path}"

        logger.info(
            "Generated %d load(s), %d BC(s), %d material(s) "
            "for project '%s' [id=%s] [mode=%s] → saved to %s",
            len(parameter_set.loads),
            len(parameter_set.boundary_conditions),
            len(parameter_set.materials),
            request.project_name,
            response.request_id,
            mode.value,
            local_path,
        )

        return response

    except ValueError as e:
        logger.warning("Validation error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not parse constraints: {e}",
        )
    except Exception as e:
        logger.exception("Unexpected error during parameter generation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {e}",
        )


# ── Results Endpoints ────────────────────────────────────────────────

results_router = APIRouter(prefix="/api/results", tags=["Results"])


@results_router.get(
    "",
    summary="List all saved generation results",
    response_model=dict,
)
async def list_all_results(
    limit: int = Query(default=50, ge=1, le=200, description="Max results to return"),
):
    """Return a list of all previously generated results, newest first."""
    results = list_results(limit=limit)
    return {"count": len(results), "results": results}


@results_router.get(
    "/{request_id}",
    summary="Retrieve a specific generation result",
    response_model=dict,
)
async def get_result_by_id(request_id: str):
    """Retrieve the full parameter set for a previous generation."""
    result = get_result(request_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Result '{request_id}' not found.",
        )
    return result


@results_router.delete(
    "/{request_id}",
    summary="Delete a saved generation result",
    response_model=dict,
)
async def delete_result_by_id(request_id: str):
    """Delete a specific saved result."""
    deleted = delete_result(request_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Result '{request_id}' not found.",
        )
    return {"status": "deleted", "request_id": request_id}


# ── Utility Endpoints ────────────────────────────────────────────────

@router.get(
    "/materials",
    summary="List available materials in the database",
    response_model=dict,
)
async def list_materials():
    """Return all materials available in the built-in reference library."""
    from app.services.parameter_service import MATERIAL_DATABASE

    return {
        "count": len(MATERIAL_DATABASE),
        "materials": {
            key: mat.model_dump() for key, mat in MATERIAL_DATABASE.items()
        },
    }
