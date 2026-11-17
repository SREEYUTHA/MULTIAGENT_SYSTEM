
def normalize_path(path: str) -> str:
    """Normalize trailing slashes for endpoint comparisons."""
    path = path.strip()

    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    return path


def normalize_items(items) -> set[str]:
    """Normalize a list of API contract values."""

    if not isinstance(items, list):
        return set()

    return {
        item.strip().casefold()
        for item in items
        if isinstance(item, str) and item.strip()
    }


def endpoint_key(endpoint: dict) -> tuple[str, str] | None:
    """Extract a normalized HTTP method and path."""

    method = endpoint.get("method")
    path = endpoint.get("path")

    if not isinstance(method, str) or not isinstance(path, str):
        return None

    method = method.strip().upper()
    path = normalize_path(path)

    if not method or not path.startswith("/"):
        return None

    return method, path


def validate_api_contract(
    frontend_proposal: dict,
    backend_proposal: dict,
    api_contract: dict | None = None,
) -> list[str]:
    """
    Validate endpoint coverage and complete API contract consistency.
    """

    conflicts = []

    frontend_apis = frontend_proposal.get("api_requirements", [])
    backend_endpoints = backend_proposal.get("endpoints", [])

    if not isinstance(frontend_apis, list):
        return ["Frontend api_requirements must be a list."]

    if not isinstance(backend_endpoints, list):
        return ["Backend endpoints must be a list."]

    frontend_map = {}
    backend_map = {}

    for requirement in frontend_apis:
        if not isinstance(requirement, dict):
            conflicts.append(
                "Frontend contains an invalid API requirement."
            )
            continue

        key = endpoint_key(requirement)

        if key is None:
            conflicts.append(
                "A frontend API requirement has an invalid method or path."
            )
            continue

        if key in frontend_map:
            conflicts.append(
                f"Frontend contains duplicate endpoint {key[0]} {key[1]}."
            )

        frontend_map[key] = requirement

    for endpoint in backend_endpoints:
        if not isinstance(endpoint, dict):
            conflicts.append(
                "Backend contains an invalid endpoint entry."
            )
            continue

        key = endpoint_key(endpoint)

        if key is None:
            conflicts.append(
                "A backend endpoint has an invalid method or path."
            )
            continue

        if key in backend_map:
            conflicts.append(
                f"Backend contains duplicate endpoint {key[0]} {key[1]}."
            )

        backend_map[key] = endpoint

    frontend_keys = set(frontend_map)
    backend_keys = set(backend_map)

    # Check frontend endpoint coverage.
    for method, path in sorted(frontend_keys - backend_keys):
        conflicts.append(
            f"Frontend requires {method} {path}, "
            "but no matching backend endpoint exists."
        )

    # Check shared API contract.
    if api_contract is not None:

        requirements = api_contract.get("requirements")

        if not isinstance(requirements, list) or not requirements:
            conflicts.append(
                "The shared API contract must contain a non-empty requirements list."
            )

        else:
            contract_map = {}

            for requirement in requirements:

                if not isinstance(requirement, dict):
                    conflicts.append(
                        "The shared API contract contains an invalid requirement."
                    )
                    continue

                key = endpoint_key(requirement)

                if key is None:
                    conflicts.append(
                        "The shared API contract contains an invalid method or path."
                    )
                    continue

                if key in contract_map:
                    conflicts.append(
                        f"Shared contract contains duplicate endpoint {key[0]} {key[1]}."
                    )

                contract_map[key] = requirement

            # Fields that must be preserved by both agents.
            fields_to_compare = [
                "query_parameters",
                "request_fields",
                "response_fields",
                "error_cases",
            ]

            for key, requirement in contract_map.items():

                method, path = key

                frontend = frontend_map.get(key)
                backend = backend_map.get(key)

                if frontend is None:
                    conflicts.append(
                        f"Frontend is missing mandatory endpoint {method} {path}."
                    )

                if backend is None:
                    conflicts.append(
                        f"Backend is missing mandatory endpoint {method} {path}."
                    )

                # Compare all mandatory contract fields.
                for field in fields_to_compare:

                    expected = normalize_items(
                        requirement.get(field, [])
                    )

                    if frontend is not None:
                        actual = normalize_items(
                            frontend.get(field, [])
                        )

                        missing = expected - actual

                        if missing:
                            conflicts.append(
                                f"Frontend {method} {path} is missing "
                                f"{field}: {sorted(missing)}."
                            )

                    if backend is not None:
                        actual = normalize_items(
                            backend.get(field, [])
                        )

                        missing = expected - actual

                        if missing:
                            conflicts.append(
                                f"Backend {method} {path} is missing "
                                f"{field}: {sorted(missing)}."
                            )

                # Check that endpoint purposes are consistent.
                expected_purpose = requirement.get("purpose")

                for agent_name, proposal in [
                    ("Frontend", frontend),
                    ("Backend", backend),
                ]:

                    if proposal is None:
                        continue

                    actual_purpose = proposal.get("purpose")

                    if (
                        isinstance(expected_purpose, str)
                        and isinstance(actual_purpose, str)
                        and actual_purpose.strip().casefold()
                        != expected_purpose.strip().casefold()
                    ):
                        conflicts.append(
                            f"{agent_name} {method} {path} has a "
                            "different purpose from the shared contract."
                        )

    return conflicts
