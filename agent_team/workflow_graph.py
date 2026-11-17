
from typing import TypedDict, Any

from langgraph.graph import StateGraph, START, END

from frontend_agent import propose_frontend, review_frontend
from backend_agent import propose_backend, review_backend
from testing_agent import propose_testing, review_testing
from api_contractor_validation import validate_api_contract
# from requirements_agent import create_api_contract 
from schemas import SharedAPIContract

import re
from datetime import datetime

from code_generation_agent import generate_project_files
from file_manager import write_project_files


from technology_stack_planner import plan_technology_stack


# Shared state passed between graph nodes.
class TeamState(TypedDict, total=False):
    project_idea: str
    technology_plan: dict[str, Any]
    api_contract: dict[str, Any]

    frontend: dict[str, Any]
    backend: dict[str, Any]
    testing: dict[str, Any]

    revised_frontend: dict[str, Any]
    revised_backend: dict[str, Any]
    final_testing: dict[str, Any]

    api_conflicts: list[str]
    blockers: list[str]
    all_conflicts: list[str]
    invalid_fields: list[str]

    generated_files: list[dict[str, Any]]
    project_name: str
    generated_project_path: str

    

    approved: bool
    outcome: str

def build_shared_api_contract(endpoints: list[dict]) -> dict:
    """Build the shared API contract from backend endpoints."""

    requirements = [
        {
            key: endpoint[key]
            for key in [
                "method",
                "path",
                "purpose",
                "query_parameters",
                "request_fields",
                "response_fields",
                "error_cases",
            ]
        }
        for endpoint in endpoints
    ]

    return SharedAPIContract(
        requirements=requirements
    ).model_dump()


def technology_planning_phase(state: TeamState) -> dict:

    print("\n[Technology Planner] Analyzing project requirements...")

    plan = plan_technology_stack(
        state["project_idea"]
    )

    technology_plan = plan.model_dump()

    print("\n[Technology Planner] Stack selected successfully.")

    return {
        "technology_plan": technology_plan
    }

# Node 1: Generate initial designs and initial QA review.
def proposal_phase(state: TeamState) -> dict:
    """Generate backend first, then share its API contract with the team."""

    idea = state["project_idea"]

    # Step 1: Backend Agent designs the backend independently.
    backend = propose_backend(
        idea,
        state["technology_plan"],
    )

    # Step 2: Extract the shared API contract from backend endpoints.
    requirements = [
        {
            key: endpoint[key]
            for key in [
                "method",
                "path",
                "purpose",
                "query_parameters",
                "request_fields",
                "response_fields",
                "error_cases",
            ]
        }
        for endpoint in backend["endpoints"]
    ]

    # api_contract = SharedAPIContract(
    #     requirements=requirements
    # ).model_dump()
    api_contract = build_shared_api_contract(backend["endpoints"])

    # Step 3: Frontend Agent uses the shared API contract.
    frontend = propose_frontend(
        idea,
        api_contract,
        state["technology_plan"],
    )

    # Step 4: Testing Agent reviews both proposals and the contract.
    testing = propose_testing(
        idea,
        frontend,
        backend,
        api_contract,
        state["technology_plan"],
    )
    return {
        "api_contract": api_contract,
        "backend": backend,
        "frontend": frontend,
        "testing": testing,
    }


# Node 2: Share API conflicts and revise both proposals.
def revision_phase(state: TeamState) -> dict:

    idea = state["project_idea"]
    api_contract = state["api_contract"]

    frontend = state["frontend"]
    backend = state["backend"]
    testing = state["testing"]

    print("\n[API Validator] Checking initial proposals...")

    api_conflicts = validate_api_contract(
        frontend,
        backend,
        api_contract,
    )

    frontend_feedback = {
        "backend_proposal": backend,
        "testing_report": testing,
        "api_conflicts": api_conflicts,
    }

    print("\n[Frontend Agent] Revising proposal...")

    revised_frontend = review_frontend(
    idea,
    frontend,
    frontend_feedback,
    api_contract,
    state["technology_plan"],
    )

    backend_feedback = {
        "frontend_proposal": revised_frontend,
        "testing_report": testing,
        "api_conflicts": api_conflicts,
    }

    print("\n[Backend Agent] Revising proposal...")

    revised_backend = review_backend(
    idea,
    backend,
    backend_feedback,
    api_contract,
    state["technology_plan"],
    )

    print("\n[API Contract] Regenerating contract from revised backend...")

    revised_requirements = revised_backend["endpoints"]

    # final_api_contract = SharedAPIContract(
    #     requirements=revised_requirements
    # ).model_dump()
    final_api_contract = build_shared_api_contract(
        revised_backend["endpoints"]
    )

    print("\n[API Validator] Checking revised proposals...")

    revised_api_conflicts = validate_api_contract(
        revised_frontend,
        revised_backend,
        final_api_contract,
    )

    return {
        "revised_frontend": revised_frontend,
        "revised_backend": revised_backend,
        "api_contract": final_api_contract,
        "api_conflicts": revised_api_conflicts,
    }


# Node 3: QA reviews the revised designs.
def final_qa_phase(state: TeamState) -> dict:

    print("\n[Testing Agent] Performing final QA review...")

    final_api_conflicts = validate_api_contract(
        state["revised_frontend"],
        state["revised_backend"],
        state["api_contract"],
    )

    peer_feedback = {
        "revised_frontend": state["revised_frontend"],
        "revised_backend": state["revised_backend"],
        "api_conflicts": final_api_conflicts,
    }

    final_testing = review_testing(
    state["project_idea"],
    state["testing"],
    peer_feedback,
    state["api_contract"],
    state["technology_plan"],
    )

    return {
        "final_testing": final_testing,
        "api_conflicts": final_api_conflicts,
    }


# Node 4: Decide whether the design is ready.
def readiness_phase(state: TeamState) -> dict:

    qa = state["final_testing"]

    required_lists = [
        "blockers",
        "frontend_backend_conflicts",
        "open_questions",
        "risks",
        "validation_checks",
        "security_checks",
    ]

    # invalid_fields = [
    #     field
    #     for field in required_lists
    #     if not isinstance(qa.get(field), list)
    # ]
    invalid_fields = [
        field
        for field in required_lists
        if (
            not isinstance(qa.get(field), list)
            or not all(
                isinstance(item, str) and item.strip()
                for item in qa.get(field, [])
            )
        )
    ]

    blockers = qa.get("blockers", [])
    qa_conflicts = qa.get("frontend_backend_conflicts", [])
    api_conflicts = state.get("api_conflicts", [])

    all_conflicts = qa_conflicts + api_conflicts

    approved = (
        not invalid_fields
        and not blockers
        and not all_conflicts
    )

    if invalid_fields:
        outcome = "blocked_invalid_qa_output"
    elif blockers:
        outcome = "blocked_by_qa"
    elif all_conflicts:
        outcome = "blocked_by_conflicts"
    else:
        outcome = "approved"

    return {
        "invalid_fields": invalid_fields,
        "blockers": blockers,
        "all_conflicts": all_conflicts,
        "approved": approved,
        "outcome": outcome,
    }

# Conditional routing.
def route_after_readiness(state: TeamState) -> str:

    if state.get("approved", False):
        return "approved"

    return "blocked"


# Final outcomes.
def approved_phase(state: TeamState) -> dict:
    return {"outcome": "approved"}


def blocked_phase(state: TeamState) -> dict:
    return {"outcome": "blocked"}


# Node 6: Generate and save application files.
def code_generation_phase(state: TeamState) -> dict:

    print("\n[Code Generation Agent] Generating application files...")

    generated_output = generate_project_files(
        project_idea=state["project_idea"],
        api_contract=state["api_contract"],
        frontend_proposal=state["revised_frontend"],
        backend_proposal=state["revised_backend"],
        testing_proposal=state["final_testing"],
        technology_plan=state["technology_plan"],
    )

    # Convert validated generated files into the format
    # expected by the File Manager.
    files = {
        item.path: item.content
        for item in generated_output.files
    }

    # Protect against duplicate paths before saving.
    if len(files) != len(generated_output.files):
        raise ValueError("Generated output contains duplicate file paths.")

    # Create a safe, unique project folder name.
    slug = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        state["project_idea"].lower()
    ).strip("_")[:40]

    if not slug:
        slug = "generated_app"

    project_name = (
        f"{slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    print(f"\n[File Manager] Saving {len(files)} generated files...")

    project_path = write_project_files(
        project_name,
        files
    )

    print(f"\n[File Manager] Project saved at: {project_path}")

    return {
        "generated_files": [
            {"path": path, "content": content}
            for path, content in files.items()
        ],
        "project_name": project_name,
        "generated_project_path": str(project_path),
        "outcome": "approved",
    }

# Build the graph.
builder = StateGraph(TeamState)


builder.add_node(
    "technology_planning",
    technology_planning_phase
)

builder.add_node("proposals", proposal_phase)
builder.add_node("revisions", revision_phase)
builder.add_node("final_qa", final_qa_phase)
builder.add_node("readiness", readiness_phase)
builder.add_node("approved_result", approved_phase)
builder.add_node("code_generation", code_generation_phase)
builder.add_node("blocked_result", blocked_phase)


builder.add_edge(START, "technology_planning")

builder.add_edge(
    "technology_planning",
    "proposals"
)
builder.add_edge("proposals", "revisions")
builder.add_edge("revisions", "final_qa")
builder.add_edge("final_qa", "readiness")

builder.add_conditional_edges(
    "readiness",
    route_after_readiness,
    {
        "approved": "code_generation",
        "blocked": "blocked_result",
    },
)

builder.add_edge("code_generation", END)
builder.add_edge("blocked_result", END)

team_graph = builder.compile()
