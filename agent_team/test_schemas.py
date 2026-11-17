
import pytest
from pydantic import ValidationError

from schemas import APIRequirement, APIEndpoint, SharedAPIContract


def test_valid_api_requirement():
    requirement = APIRequirement(
        method="GET",
        path="/api/items/{id}",
        purpose="Retrieve one item",
    )

    assert requirement.method == "GET"
    assert requirement.path == "/api/items/{id}"


def test_invalid_http_method_is_rejected():
    with pytest.raises(ValidationError):
        APIRequirement(
            method="FETCH",
            path="/api/items",
            purpose="Retrieve items",
        )


def test_valid_api_endpoint():
    endpoint = APIEndpoint(
        method="GET",
        path="/api/items/{id}",
        purpose="Retrieve one item",
        response_fields=["id", "name", "quantity"],
    )

    assert "quantity" in endpoint.response_fields


def test_unexpected_field_is_rejected():
    with pytest.raises(ValidationError):
        APIRequirement(
            method="GET",
            path="/api/items",
            purpose="Retrieve items",
            unexpected_field="not allowed",
        )



def test_valid_shared_api_contract():
    contract = SharedAPIContract(
        requirements=[
            {
                "method": "GET",
                "path": "/api/items",
                "purpose": "List inventory items",
            },
            {
                "method": "POST",
                "path": "/api/items",
                "purpose": "Create inventory item",
            },
        ]
    )

    assert len(contract.requirements) == 2
    assert contract.requirements[0].method == "GET"


def test_invalid_shared_api_contract():
    with pytest.raises(ValidationError):
        SharedAPIContract(
            requirements=[
                {
                    "method": "FETCH",
                    "path": "/api/items",
                    "purpose": "List inventory items",
                }
            ]
        )
