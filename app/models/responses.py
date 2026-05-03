"""
GenBuilder — Response Models

Defines the structured output schemas that are consumable by
generative design solvers (e.g., Altair Inspire, nTopology, Fusion 360).
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


# ── Enums ─────────────────────────────────────────────────────────────

class LoadType(str, Enum):
    """Supported mechanical load types."""
    TENSILE = "tensile"
    COMPRESSIVE = "compressive"
    SHEAR = "shear"
    BENDING = "bending"
    TORSIONAL = "torsional"
    DISTRIBUTED = "distributed"
    POINT = "point"


class ConstraintType(str, Enum):
    """Boundary constraint degrees of freedom."""
    FIXED = "fixed"
    PINNED = "pinned"
    ROLLER = "roller"
    SLIDING = "sliding"
    SYMMETRY = "symmetry"


class SolverType(str, Enum):
    """Target generative design solver."""
    TOPOLOGY_OPTIMIZATION = "topology_optimization"
    LATTICE = "lattice"
    SHAPE = "shape"


# ── Sub-Models ────────────────────────────────────────────────────────

class Vector3D(BaseModel):
    """A 3D vector used for load directions, positions, and normals."""
    x: float = Field(0.0, description="X component")
    y: float = Field(0.0, description="Y component")
    z: float = Field(0.0, description="Z component")


class LoadCondition(BaseModel):
    """
    A single mechanical load applied to the design space.

    Captures magnitude, direction, application region, and load type
    in a format directly mappable to solver input files.
    """

    load_type: LoadType = Field(
        ..., description="Category of the applied load."
    )
    magnitude_n: float = Field(
        ..., gt=0, description="Load magnitude in Newtons."
    )
    direction: Vector3D = Field(
        default_factory=lambda: Vector3D(x=0, y=-1, z=0),
        description="Unit direction vector of the load.",
    )
    application_region: str = Field(
        ...,
        description=(
            "Human-readable description of where the load is applied "
            "(e.g., 'right edge', 'top surface center')."
        ),
    )


class MaterialProperties(BaseModel):
    """
    Material properties extracted from the user's description.

    Values are in SI units (Pa for stresses, kg/m³ for density).
    """

    name: str = Field(
        ..., description="Material name (e.g., 'Aluminum 6061-T6')."
    )
    youngs_modulus_pa: float = Field(
        ..., gt=0, description="Young's modulus (elastic modulus) in Pascals."
    )
    yield_strength_pa: float = Field(
        ..., gt=0, description="Yield strength in Pascals."
    )
    density_kg_m3: float = Field(
        ..., gt=0, description="Density in kg/m³."
    )
    poissons_ratio: float = Field(
        ..., gt=0, lt=0.5, description="Poisson's ratio (dimensionless)."
    )
    ultimate_tensile_strength_pa: Optional[float] = Field(
        None, gt=0, description="Ultimate tensile strength in Pascals."
    )


class BoundaryCondition(BaseModel):
    """
    A single boundary condition (constraint) applied to the design.

    Specifies which region is constrained and the type of constraint.
    """

    constraint_type: ConstraintType = Field(
        ..., description="Type of boundary constraint."
    )
    constrained_region: str = Field(
        ...,
        description=(
            "Human-readable description of the constrained geometry "
            "(e.g., 'two bolt holes on left face')."
        ),
    )
    fixed_dof: list[str] = Field(
        default_factory=lambda: ["Tx", "Ty", "Tz", "Rx", "Ry", "Rz"],
        description=(
            "Degrees of freedom that are fixed. "
            "T = translation, R = rotation; x/y/z = axis."
        ),
    )


class ObjectiveSettings(BaseModel):
    """Optimization objective and constraints for the solver."""

    objective: str = Field(
        default="minimize_mass",
        description=(
            "Optimization objective: minimize_mass, maximize_stiffness, "
            "or minimize_compliance."
        ),
    )
    safety_factor: float = Field(
        default=2.0, gt=0, description="Minimum required safety factor."
    )
    max_mass_kg: Optional[float] = Field(
        None, gt=0, description="Maximum allowable mass in kg."
    )
    volume_fraction: Optional[float] = Field(
        None,
        gt=0,
        le=1.0,
        description="Target volume fraction (0-1) for topology optimization.",
    )


# ── Top-Level Structured Output ──────────────────────────────────────

class DesignParameterSet(BaseModel):
    """
    The fully structured parameter set ready for a generative design solver.

    This is the core output of the GenBuilder pipeline — a bridge between
    natural language designer intent and machine-readable solver config.
    """

    project_name: str
    solver_type: SolverType
    materials: list[MaterialProperties]
    loads: list[LoadCondition]
    boundary_conditions: list[BoundaryCondition]
    objectives: ObjectiveSettings
    raw_constraints_text: str = Field(
        ..., description="Original user input preserved for traceability."
    )


class DesignResponse(BaseModel):
    """
    The final API response wrapping the design parameter set
    along with metadata.
    """

    request_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique ID for this generation request.",
    )
    status: str = Field(
        default="completed",
        description="Processing status: completed, partial, or error.",
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp of when the response was created.",
    )
    parameters: DesignParameterSet = Field(
        ..., description="The generated structured design parameters."
    )
    s3_uri: Optional[str] = Field(
        None,
        description="S3 URI where the parameter JSON was uploaded (if enabled).",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    "status": "completed",
                    "created_at": "2026-05-04T00:00:00+00:00",
                    "parameters": {
                        "project_name": "bracket-v1",
                        "solver_type": "topology_optimization",
                        "materials": [
                            {
                                "name": "Aluminum 6061-T6",
                                "youngs_modulus_pa": 68.9e9,
                                "yield_strength_pa": 276e6,
                                "density_kg_m3": 2710.0,
                                "poissons_ratio": 0.33,
                                "ultimate_tensile_strength_pa": 310e6,
                            }
                        ],
                        "loads": [
                            {
                                "load_type": "tensile",
                                "magnitude_n": 500.0,
                                "direction": {"x": 1.0, "y": 0.0, "z": 0.0},
                                "application_region": "right edge",
                            }
                        ],
                        "boundary_conditions": [
                            {
                                "constraint_type": "fixed",
                                "constrained_region": "two bolt holes on left face",
                                "fixed_dof": ["Tx", "Ty", "Tz", "Rx", "Ry", "Rz"],
                            }
                        ],
                        "objectives": {
                            "objective": "minimize_mass",
                            "safety_factor": 2.0,
                            "max_mass_kg": None,
                            "volume_fraction": 0.3,
                        },
                        "raw_constraints_text": "Design a lightweight aluminum bracket...",
                    },
                    "s3_uri": None,
                }
            ]
        }
    )
