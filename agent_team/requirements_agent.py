
import json

from pydantic import ValidationError

from llm_client import ask_llm
from schemas import SharedAPIContract



REQUIREMENTS_SYSTEM_PROMPT = """
You are a senior software architect.

Convert the user's application idea into a shared API contract
for frontend and backend development.

Return exactly one valid JSON object:

{
  "requirements": [
    {
      "method": "GET",
      "path": "/api/example",
      "purpose": "Short purpose"
    }
  ]
}

Rules:
- Identify all essential APIs based on the application idea.
- Use GET, POST, PUT, PATCH, or DELETE.
- Every path must start with "/".
- Use consistent REST API conventions.
- Use POST for login requests submitting credentials.
- Avoid unrelated features and duplicate endpoints.
- Keep purposes concise.
- Return valid JSON only, without Markdown.
"""


def create_api_contract(project_idea: str) -> dict:
    """Generate and validate the shared API contract."""

    prompt = f"""
APPLICATION IDEA:
{project_idea}

Identify the essential API endpoints needed to satisfy the application
requirements. Return the complete contract using the required schema.
"""

    response = ask_llm(REQUIREMENTS_SYSTEM_PROMPT, prompt)
    response = response.strip()

    # Extract the JSON object.
    start = response.find("{")
    end = response.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError(
            "Requirements Agent returned no complete JSON object."
        )

    try:
        data = json.loads(response[start:end + 1])
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Requirements Agent returned invalid JSON: {exc}"
        ) from exc

    # Normalize HTTP methods.
    if isinstance(data, dict):
        requirements = data.get("requirements", [])

        if isinstance(requirements, list):
            for requirement in requirements:
                if isinstance(requirement, dict):
                    method = requirement.get("method")

                    if isinstance(method, str):
                        requirement["method"] = method.strip().upper()

    try:
        contract = SharedAPIContract.model_validate(data)
    except ValidationError as exc:
        raise ValueError(
            f"API contract schema validation failed: {exc}"
        ) from exc

    return contract.model_dump()
