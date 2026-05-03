"""
GenBuilder — Crew Orchestrator

Wires the Constraint Parser and Parameter Formatter agents into a
sequential CrewAI pipeline. The output is a solver-ready JSON string.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import numpy as np
from crewai import Crew, Process, Task

from app.agents.constraint_parser import create_constraint_parser_agent
from app.agents.parameter_formatter import create_parameter_formatter_agent
from app.models.responses import (
    BoundaryCondition,
    ConstraintType,
    DesignParameterSet,
    LoadCondition,
    LoadType,
    MaterialProperties,
    ObjectiveSettings,
    SolverType,
    Vector3D,
)
from app.services.parameter_service import (
    MATERIAL_DATABASE,
    generate_parameters as heuristic_generate,
)

logger = logging.getLogger(__name__)


# ── Helper: Parse LLM JSON output ────────────────────────────────────

def _clean_json_string(raw: str) -> str:
    """Strip markdown fences and whitespace from LLM output."""
    text = raw.strip()
    # Remove ```json ... ``` wrapping
    if text.startswith("```"):
        lines = text.split("\n")
        # Drop first and last lines (the fences)
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return text.strip()


def _normalize_direction(direction: dict) -> dict:
    """Normalize a direction vector to unit length using NumPy."""
    vec = np.array([
        float(direction.get("x", 0)),
        float(direction.get("y", -1)),
        float(direction.get("z", 0)),
    ])
    norm = float(np.linalg.norm(vec))
    if norm > 0:
        vec = vec / norm
    return {"x": float(vec[0]), "y": float(vec[1]), "z": float(vec[2])}


def _parse_llm_output(
    raw_output: str,
    project_name: str,
    solver_type: str,
    original_text: str,
) -> DesignParameterSet:
    """
    Parse the JSON string from the LLM into a validated DesignParameterSet.

    Falls back to heuristic parsing if the LLM output is malformed.
    """
    try:
        cleaned = _clean_json_string(raw_output)
        data = json.loads(cleaned)

        # ── Materials ─────────────────────────────────────
        materials = []
        for mat in data.get("materials", []):
            materials.append(
                MaterialProperties(
                    name=mat["name"],
                    youngs_modulus_pa=float(mat["youngs_modulus_pa"]),
                    yield_strength_pa=float(mat["yield_strength_pa"]),
                    density_kg_m3=float(mat["density_kg_m3"]),
                    poissons_ratio=float(mat["poissons_ratio"]),
                    ultimate_tensile_strength_pa=mat.get(
                        "ultimate_tensile_strength_pa"
                    ),
                )
            )
        if not materials:
            materials = [MATERIAL_DATABASE["steel"]]

        # ── Loads ─────────────────────────────────────────
        loads = []
        for load in data.get("loads", []):
            direction = _normalize_direction(
                load.get("direction", {"x": 0, "y": -1, "z": 0})
            )
            loads.append(
                LoadCondition(
                    load_type=LoadType(load.get("load_type", "point")),
                    magnitude_n=float(load["magnitude_n"]),
                    direction=Vector3D(**direction),
                    application_region=load.get(
                        "application_region", "unspecified"
                    ),
                )
            )
        if not loads:
            loads = [
                LoadCondition(
                    load_type=LoadType.POINT,
                    magnitude_n=1000.0,
                    direction=Vector3D(x=0, y=-1, z=0),
                    application_region="unspecified — default",
                )
            ]

        # ── Boundary Conditions ───────────────────────────
        bcs = []
        for bc in data.get("boundary_conditions", []):
            ct = bc.get("constraint_type", "fixed")
            bcs.append(
                BoundaryCondition(
                    constraint_type=ConstraintType(ct),
                    constrained_region=bc.get(
                        "constrained_region", "unspecified"
                    ),
                    fixed_dof=bc.get(
                        "fixed_dof",
                        ["Tx", "Ty", "Tz", "Rx", "Ry", "Rz"],
                    ),
                )
            )
        if not bcs:
            bcs = [
                BoundaryCondition(
                    constraint_type=ConstraintType.FIXED,
                    constrained_region="unspecified — default",
                )
            ]

        # ── Objectives ────────────────────────────────────
        obj_data = data.get("objectives", {})
        objectives = ObjectiveSettings(
            objective=obj_data.get("objective", "minimize_mass"),
            safety_factor=float(obj_data.get("safety_factor", 2.0)),
            max_mass_kg=(
                float(obj_data["max_mass_kg"])
                if obj_data.get("max_mass_kg") is not None
                else None
            ),
            volume_fraction=(
                float(obj_data["volume_fraction"])
                if obj_data.get("volume_fraction") is not None
                else None
            ),
        )

        # ── Solver Type ───────────────────────────────────
        solver_str = data.get("solver_type", solver_type)
        solver_map = {
            "topology_optimization": SolverType.TOPOLOGY_OPTIMIZATION,
            "lattice": SolverType.LATTICE,
            "shape": SolverType.SHAPE,
        }
        solver = solver_map.get(solver_str, SolverType.TOPOLOGY_OPTIMIZATION)

        return DesignParameterSet(
            project_name=data.get("project_name", project_name),
            solver_type=solver,
            materials=materials,
            loads=loads,
            boundary_conditions=bcs,
            objectives=objectives,
            raw_constraints_text=original_text,
        )

    except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
        logger.warning(
            "LLM output parsing failed (%s). Falling back to heuristic parser.",
            str(e),
        )
        return heuristic_generate(
            description=original_text,
            project_name=project_name,
            solver_type=solver_type,
        )


# ── Public API ────────────────────────────────────────────────────────

def run_design_crew(
    description: str,
    project_name: str,
    solver_type: str,
) -> DesignParameterSet:
    """
    Execute the two-agent CrewAI pipeline:

    1. Constraint Parser — reads natural language, extracts constraints.
    2. Parameter Formatter — structures constraints into solver-ready JSON.

    Falls back to heuristic parsing if the LLM is unavailable or errors.
    """
    try:
        # ── Create agents ─────────────────────────────────
        parser_agent = create_constraint_parser_agent()
        formatter_agent = create_parameter_formatter_agent()

        # ── Define tasks ──────────────────────────────────
        parse_task = Task(
            description=(
                f"Analyze the following engineering design description and "
                f"extract ALL constraints including:\n"
                f"- Material(s) and their properties\n"
                f"- Load(s): type, magnitude (in Newtons), direction, "
                f"application region\n"
                f"- Boundary condition(s): type, constrained region, DOF\n"
                f"- Optimization objectives: goal, safety factor, mass limits\n"
                f"- Solver type preference\n\n"
                f"--- DESCRIPTION ---\n{description}\n--- END ---\n\n"
                f"Project name: {project_name}\n"
                f"Requested solver: {solver_type}\n\n"
                f"List every constraint you find with precise values. "
                f"If a standard material is mentioned, include its full "
                f"mechanical properties (E, σ_y, ρ, ν, UTS) in SI units."
            ),
            expected_output=(
                "A detailed list of all extracted engineering constraints "
                "with precise numerical values in SI units."
            ),
            agent=parser_agent,
        )

        format_task = Task(
            description=(
                "Using the extracted constraints from the previous analysis, "
                "produce a single valid JSON object matching the solver input "
                "schema. Rules:\n"
                "1. All stress/modulus values in Pascals (Pa)\n"
                "2. Density in kg/m³\n"
                "3. Load magnitudes in Newtons (N)\n"
                "4. Direction vectors must be normalized to unit length\n"
                "5. Include all 6 DOF for fixed constraints\n"
                "6. Use these exact enum values:\n"
                "   - load_type: tensile, compressive, shear, bending, "
                "torsional, distributed, point\n"
                "   - constraint_type: fixed, pinned, roller, sliding, symmetry\n"
                "   - solver_type: topology_optimization, lattice, shape\n"
                "   - objective: minimize_mass, maximize_stiffness, "
                "minimize_compliance\n\n"
                "Return ONLY the raw JSON. No markdown, no explanation."
            ),
            expected_output=(
                "A single valid JSON object with keys: project_name, "
                "solver_type, materials, loads, boundary_conditions, objectives."
            ),
            agent=formatter_agent,
        )

        # ── Assemble and run the crew ─────────────────────
        crew = Crew(
            agents=[parser_agent, formatter_agent],
            tasks=[parse_task, format_task],
            process=Process.sequential,
            verbose=True,
        )

        logger.info("Starting CrewAI pipeline for project '%s'", project_name)
        result = crew.kickoff()

        # CrewAI returns a CrewOutput object — get the raw string
        raw_output = str(result)
        logger.info(
            "CrewAI pipeline completed. Output length: %d chars",
            len(raw_output),
        )

        return _parse_llm_output(
            raw_output=raw_output,
            project_name=project_name,
            solver_type=solver_type,
            original_text=description,
        )

    except Exception as e:
        logger.error(
            "CrewAI pipeline failed: %s. Falling back to heuristic parser.",
            str(e),
        )
        return heuristic_generate(
            description=description,
            project_name=project_name,
            solver_type=solver_type,
        )
