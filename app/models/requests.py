"""
GenBuilder — Request Models

Defines the Pydantic schemas for incoming API requests.
"""

from pydantic import BaseModel, ConfigDict, Field


class DesignRequest(BaseModel):
    """
    The user-facing input payload.

    Users describe their engineering constraints in plain English,
    and optionally provide a project name to tag the output.
    """

    description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description=(
            "Natural language description of the engineering design constraints. "
            "Should include information about loads, materials, boundary conditions, "
            "dimensions, and safety factors."
        ),
        json_schema_extra={
            "examples": [
                "Design a lightweight aluminum bracket that can withstand 500N "
                "of tensile load. The part is fixed at two bolt holes on the left "
                "face and the load is applied on the right edge. Minimum safety "
                "factor of 2.0."
            ]
        },
    )

    project_name: str = Field(
        default="untitled-project",
        max_length=100,
        pattern=r"^[a-zA-Z0-9_\- ]+$",
        description="A short, slug-friendly name for this design project.",
    )

    solver_type: str = Field(
        default="topology_optimization",
        description="Target solver type: topology_optimization, lattice, or shape.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "description": (
                        "Design a steel mounting plate for a 1kN vertical load. "
                        "The plate is bolted at four corners and the load is applied "
                        "at the center. Use AISI 1045 steel. Target mass under 2 kg. "
                        "Safety factor of 3.0."
                    ),
                    "project_name": "mounting-plate-v2",
                    "solver_type": "topology_optimization",
                }
            ]
        }
    )
