
from api_contractor_validation import validate_api_contract


def test_matching_frontend_and_backend_endpoints():
    frontend = {
        "api_requirements": [
            {
                "method": "GET",
                "path": "/api/items",
                "purpose": "List items",
            }
        ]
    }

    backend = {
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/items",
                "purpose": "List items",
            }
        ]
    }

    conflicts = validate_api_contract(frontend, backend)

    assert conflicts == []


def test_mismatched_http_methods_are_detected():
    frontend = {
        "api_requirements": [
            {
                "method": "GET",
                "path": "/api/products",
                "purpose": "List products",
            }
        ]
    }

    backend = {
        "endpoints": [
            {
                "method": "POST",
                "path": "/api/products",
                "purpose": "Create a product",
            }
        ]
    }

    conflicts = validate_api_contract(frontend, backend)

    assert any("GET /api/products" in conflict for conflict in conflicts)


def test_missing_frontend_contract_endpoint_is_detected():
    frontend = {"api_requirements": []}

    backend = {
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/items",
                "purpose": "List items",
            }
        ]
    }

    contract = {
        "requirements": [
            {
                "method": "GET",
                "path": "/api/items",
                "purpose": "List items",
            }
        ]
    }

    conflicts = validate_api_contract(frontend, backend, contract)

    assert any("Frontend is missing mandatory endpoint" in item for item in conflicts)


def test_missing_backend_contract_endpoint_is_detected():
    frontend = {
        "api_requirements": [
            {
                "method": "GET",
                "path": "/api/items",
                "purpose": "List items",
            }
        ]
    }

    backend = {"endpoints": []}

    contract = {
        "requirements": [
            {
                "method": "GET",
                "path": "/api/items",
                "purpose": "List items",
            }
        ]
    }

    conflicts = validate_api_contract(frontend, backend, contract)

    assert any("Backend is missing mandatory endpoint" in item for item in conflicts)
