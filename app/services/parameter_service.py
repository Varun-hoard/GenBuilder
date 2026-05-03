"""
GenBuilder — Parameter Generation Service

Phase 1: Rule-based heuristic parser that extracts structured parameters
from natural language. This will be replaced by CrewAI agents in Phase 2.
"""

from __future__ import annotations

import re
from typing import Optional

import numpy as np

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


# ── Material Library ──────────────────────────────────────────────────
# A reference lookup table for common engineering materials.

MATERIAL_DATABASE: dict[str, MaterialProperties] = {
    "aluminum": MaterialProperties(
        name="Aluminum 6061-T6",
        youngs_modulus_pa=68.9e9,
        yield_strength_pa=276e6,
        density_kg_m3=2710.0,
        poissons_ratio=0.33,
        ultimate_tensile_strength_pa=310e6,
    ),
    "steel": MaterialProperties(
        name="AISI 1045 Steel",
        youngs_modulus_pa=200e9,
        yield_strength_pa=530e6,
        density_kg_m3=7850.0,
        poissons_ratio=0.29,
        ultimate_tensile_strength_pa=625e6,
    ),
    "titanium": MaterialProperties(
        name="Ti-6Al-4V (Grade 5)",
        youngs_modulus_pa=113.8e9,
        yield_strength_pa=880e6,
        density_kg_m3=4430.0,
        poissons_ratio=0.34,
        ultimate_tensile_strength_pa=950e6,
    ),
    "copper": MaterialProperties(
        name="C11000 Copper",
        youngs_modulus_pa=117e9,
        yield_strength_pa=69e6,
        density_kg_m3=8960.0,
        poissons_ratio=0.34,
        ultimate_tensile_strength_pa=220e6,
    ),
    "abs": MaterialProperties(
        name="ABS Plastic",
        youngs_modulus_pa=2.3e9,
        yield_strength_pa=43e6,
        density_kg_m3=1050.0,
        poissons_ratio=0.39,
        ultimate_tensile_strength_pa=44e6,
    ),
    "nylon": MaterialProperties(
        name="Nylon 6/6",
        youngs_modulus_pa=2.7e9,
        yield_strength_pa=70e6,
        density_kg_m3=1140.0,
        poissons_ratio=0.39,
        ultimate_tensile_strength_pa=85e6,
    ),
}


# ── Heuristic Parser ─────────────────────────────────────────────────

def _detect_material(text: str) -> MaterialProperties:
    """Find the first matching material in the description."""
    text_lower = text.lower()
    for keyword, material in MATERIAL_DATABASE.items():
        if keyword in text_lower:
            return material
    # Default to steel if nothing detected
    return MATERIAL_DATABASE["steel"]


def _extract_loads(text: str) -> list[LoadCondition]:
    """
    Extract load magnitude and type from the description using
    regex heuristics.
    """
    loads: list[LoadCondition] = []
    text_lower = text.lower()

    # Match patterns like "500N", "1 kN", "2.5 MN"
    magnitude_pattern = r"(\d+(?:\.\d+)?)\s*(mn|kn|n)\b"
    matches = re.findall(magnitude_pattern, text_lower)

    for value_str, unit in matches:
        value = float(value_str)
        multiplier = {"n": 1.0, "kn": 1e3, "mn": 1e6}.get(unit, 1.0)
        magnitude = value * multiplier

        # Determine load type
        load_type = LoadType.POINT
        for lt in LoadType:
            if lt.value in text_lower:
                load_type = lt
                break

        # Determine direction based on context keywords
        direction = Vector3D(x=0, y=-1, z=0)  # default: gravity direction
        if "horizontal" in text_lower or "tensile" in text_lower:
            direction = Vector3D(x=1, y=0, z=0)
        if "vertical" in text_lower or "compressive" in text_lower:
            direction = Vector3D(x=0, y=-1, z=0)

        # Normalize direction using NumPy
        dir_array = np.array([direction.x, direction.y, direction.z])
        norm = float(np.linalg.norm(dir_array))
        if norm > 0:
            dir_array = dir_array / norm
            direction = Vector3D(
                x=float(dir_array[0]),
                y=float(dir_array[1]),
                z=float(dir_array[2]),
            )

        # Try to find application region
        region = "unspecified region"
        region_patterns = [
            r"(?:applied\s+(?:on|at|to)\s+(?:the\s+)?)([\w\s]+?)(?:\.|,|$)",
            r"(?:load\s+(?:on|at)\s+(?:the\s+)?)([\w\s]+?)(?:\.|,|$)",
        ]
        for pat in region_patterns:
            match = re.search(pat, text_lower)
            if match:
                region = match.group(1).strip()
                break

        loads.append(
            LoadCondition(
                load_type=load_type,
                magnitude_n=magnitude,
                direction=direction,
                application_region=region,
            )
        )

    # Fallback if no loads were parsed
    if not loads:
        loads.append(
            LoadCondition(
                load_type=LoadType.POINT,
                magnitude_n=1000.0,
                direction=Vector3D(x=0, y=-1, z=0),
                application_region="unspecified — using default 1 kN downward",
            )
        )

    return loads


def _extract_boundary_conditions(text: str) -> list[BoundaryCondition]:
    """Extract boundary conditions from the description."""
    bcs: list[BoundaryCondition] = []
    text_lower = text.lower()

    # Detect constraint type
    constraint_type = ConstraintType.FIXED
    for ct in ConstraintType:
        if ct.value in text_lower:
            constraint_type = ct
            break

    # Try to extract constrained region
    region = "unspecified region"
    bc_patterns = [
        r"(?:fixed\s+at\s+(?:the\s+)?)([\w\s]+?)(?:\.|,|and\s+the|$)",
        r"(?:bolted\s+at\s+(?:the\s+)?)([\w\s]+?)(?:\.|,|and\s+the|$)",
        r"(?:clamped\s+at\s+(?:the\s+)?)([\w\s]+?)(?:\.|,|and\s+the|$)",
        r"(?:constrained\s+at\s+(?:the\s+)?)([\w\s]+?)(?:\.|,|and\s+the|$)",
    ]
    for pat in bc_patterns:
        match = re.search(pat, text_lower)
        if match:
            region = match.group(1).strip()
            break

    # Set DOF based on constraint type
    dof_map: dict[ConstraintType, list[str]] = {
        ConstraintType.FIXED: ["Tx", "Ty", "Tz", "Rx", "Ry", "Rz"],
        ConstraintType.PINNED: ["Tx", "Ty", "Tz"],
        ConstraintType.ROLLER: ["Ty"],
        ConstraintType.SLIDING: ["Ty", "Tz"],
        ConstraintType.SYMMETRY: ["Tx", "Ry", "Rz"],
    }

    bcs.append(
        BoundaryCondition(
            constraint_type=constraint_type,
            constrained_region=region,
            fixed_dof=dof_map.get(
                constraint_type,
                ["Tx", "Ty", "Tz", "Rx", "Ry", "Rz"],
            ),
        )
    )

    return bcs


def _extract_objectives(text: str) -> ObjectiveSettings:
    """Extract optimization objectives and constraints."""
    text_lower = text.lower()

    # Safety factor
    safety_factor = 2.0
    sf_match = re.search(
        r"safety\s+factor\s+(?:of\s+)?(\d+(?:\.\d+)?)", text_lower
    )
    if sf_match:
        safety_factor = float(sf_match.group(1))

    # Max mass
    max_mass: Optional[float] = None
    mass_match = re.search(
        r"(?:mass|weight)\s+(?:under|below|less\s+than|max(?:imum)?)\s+(\d+(?:\.\d+)?)\s*(kg|g)",
        text_lower,
    )
    if mass_match:
        max_mass = float(mass_match.group(1))
        if mass_match.group(2) == "g":
            max_mass /= 1000.0

    # Objective
    objective = "minimize_mass"
    if "stiffness" in text_lower or "stiff" in text_lower:
        objective = "maximize_stiffness"
    elif "compliance" in text_lower:
        objective = "minimize_compliance"
    elif "lightweight" in text_lower or "light" in text_lower:
        objective = "minimize_mass"

    return ObjectiveSettings(
        objective=objective,
        safety_factor=safety_factor,
        max_mass_kg=max_mass,
        volume_fraction=0.3,  # sensible default
    )


def _resolve_solver_type(solver_str: str) -> SolverType:
    """Map user-provided solver string to enum."""
    mapping = {
        "topology_optimization": SolverType.TOPOLOGY_OPTIMIZATION,
        "topology": SolverType.TOPOLOGY_OPTIMIZATION,
        "lattice": SolverType.LATTICE,
        "shape": SolverType.SHAPE,
    }
    return mapping.get(solver_str.lower(), SolverType.TOPOLOGY_OPTIMIZATION)


# ── Public API ────────────────────────────────────────────────────────

def generate_parameters(
    description: str,
    project_name: str,
    solver_type: str,
) -> DesignParameterSet:
    """
    Parse a natural language engineering description into a
    structured DesignParameterSet.

    This Phase 1 implementation uses regex heuristics and a material
    lookup table. Phase 2 will replace the internals with CrewAI agents.
    """

    material = _detect_material(description)
    loads = _extract_loads(description)
    boundary_conditions = _extract_boundary_conditions(description)
    objectives = _extract_objectives(description)
    solver = _resolve_solver_type(solver_type)

    return DesignParameterSet(
        project_name=project_name,
        solver_type=solver,
        materials=[material],
        loads=loads,
        boundary_conditions=boundary_conditions,
        objectives=objectives,
        raw_constraints_text=description,
    )
