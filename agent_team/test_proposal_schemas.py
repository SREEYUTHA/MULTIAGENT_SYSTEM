
import pytest
from pydantic import ValidationError

from schemas import FrontendProposal, BackendProposal, TestingProposal


def test_valid_frontend_proposal():
    frontend = FrontendProposal(
        summary="Inventory dashboard",
        framework="React",
        pages=["Product list"],
        components=["Product table"],
        user_workflows=["View available stock"],
        api_requirements=[
            {
                "method": "GET",
                "path": "/api/products",
                "purpose": "List products",
            }
        ],
        accessibility=[],
        assumptions=[],
        risks=[],
        feedback_review=[],
        open_questions=[],
    )

    assert frontend.agent == "Frontend Developer"
    assert frontend.framework == "React"


def test_invalid_nested_api_requirement_is_rejected():
    with pytest.raises(ValidationError):
        FrontendProposal(
            summary="Inventory dashboard",
            framework="React",
            pages=[],
            components=[],
            user_workflows=[],
            api_requirements=[
                {
                    "method": "FETCH",
                    "path": "/api/products",
                    "purpose": "List products",
                }
            ],
            accessibility=[],
            assumptions=[],
            risks=[],
            feedback_review=[],
            open_questions=[],
        )
