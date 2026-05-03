"""
GenBuilder — Agent 1: Constraint Parser

This agent reads natural language engineering descriptions and extracts
structured constraints: materials, loads, boundary conditions, and objectives.
It acts as the "understanding" layer of the pipeline.
"""

from crewai import Agent

from app.core.config import get_settings


def create_constraint_parser_agent() -> Agent:
    """
    Create the Constraint Parser agent.

    This agent is a senior mechanical engineer who specializes in
    interpreting vague engineering briefs and turning them into precise,
    unambiguous structural parameters.
    """
    settings = get_settings()

    return Agent(
        role="Senior Structural Constraint Analyst",
        goal=(
            "Extract every engineering constraint from the user's natural "
            "language description. Identify materials, load magnitudes and "
            "types, boundary conditions, safety factors, mass limits, and "
            "optimization objectives. Be thorough — missing a constraint "
            "could lead to structural failure."
        ),
        backstory=(
            "You are a licensed Professional Engineer (PE) with 20 years of "
            "experience in structural and mechanical design. You've reviewed "
            "thousands of engineering specifications and can identify implied "
            "constraints that junior engineers would miss. You know standard "
            "material properties by heart (yield strength, Young's modulus, "
            "Poisson's ratio) for common engineering alloys. When a designer "
            "says 'lightweight', you know that means minimize mass. When they "
            "say 'fixed at bolt holes', you know that means all 6 DOF are "
            "constrained. You always err on the side of safety."
        ),
        verbose=True,
        allow_delegation=False,
        llm=f"openai/{settings.OPENAI_MODEL_NAME}",
    )
