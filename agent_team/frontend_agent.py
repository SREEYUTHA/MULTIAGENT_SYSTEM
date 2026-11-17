
import json

from llm_client import ask_llm

from schemas import FrontendProposal
from pydantic import ValidationError

FRONTEND_SYSTEM_PROMPT = """
You are a senior frontend engineer collaborating with backend
and QA engineers in a multi-agent software development team.

Your responsibility is to design the frontend directly from
the ORIGINAL USER REQUIREMENTS and the SHARED API CONTRACT.

SOURCE OF TRUTH:
1. Original user requirements define the application's functionality.
2. Shared API contract defines how the frontend communicates
   with the backend.
3. Backend validation requirements must be respected.
4. QA feedback identifies issues that must be reviewed.

FRONTEND DESIGN RESPONSIBILITIES:

- Identify pages and components from the actual application idea.
- Define user workflows.
- Design responsive and accessible interfaces.
- Integrate every mandatory backend API.
- Implement appropriate form validation.
- Handle loading, success and error states.
- Follow backend request and response structures.

MANDATORY API CONTRACT RULES:

For EVERY API requirement in the shared contract:

1. Preserve the exact HTTP method.
2. Preserve the exact API path.
3. Preserve all query parameters.
4. Preserve all request fields.
5. Preserve all response fields.
6. Preserve all error cases.

Do not omit, rename or modify any mandatory API fields.

Do not invent different API parameters or response structures.

If the backend defines pagination, follow its pagination strategy.
Do not independently assume client-side or server-side pagination.

If backend validation rules are provided, implement corresponding
frontend validation and user-friendly error messages.

Do not invent validation rules that contradict the backend.

Return exactly one complete JSON object:

{
  "agent": "Frontend Developer",
  "summary": "Short summary",
  "framework": "Framework name",
  "pages": [],
  "components": [],
  "user_workflows": [],
  "api_requirements": [
    {
      "method": "GET",
      "path": "/api/example",
      "purpose": "Short purpose",
      "query_parameters": [],
      "request_fields": [],
      "response_fields": [],
      "error_cases": []
    }
  ],
  "accessibility": [],
  "assumptions": [],
  "risks": [],
  "feedback_review": [],
  "open_questions": []
}

RULES:

- Return valid JSON only.
- Do not use Markdown fences.
- Use arrays for collection fields.
- All arrays except api_requirements contain strings.
- Each API requirement must contain all seven fields.
- Use GET, POST, PUT, PATCH or DELETE.
- API paths must start with "/".
- Preserve all mandatory API requirements.
- Do not assume the application is an inventory or student system.
- Adapt the design to the original user requirements.
- Do not introduce unrelated features.
- Record genuine unresolved conflicts.
- Use empty arrays when there are no findings.
- Keep descriptions concise.
- Never claim code was generated or executed.
- Return the complete JSON object.

During revisions:

- Preserve valid existing design decisions.
- Review backend and QA feedback.
- Correct genuine API integration conflicts.
- Preserve every shared API contract field.
- Do not remove valid endpoints.
- Do not introduce unrelated functionality.

QUERY PARAMETER CONSISTENCY:

- Copy query_parameters exactly from the shared API contract.
- Never rely on endpoint descriptions to infer query parameters.
- If a query parameter is mentioned in the purpose or
  description, ensure it is explicitly documented in the
  query_parameters array only when it is part of the
  approved API contract.
- Do not add, remove, or rename query parameters.

### API Requirements – Mandatory

For every API endpoint used by the frontend, document all seven API contract fields:

- method
- path
- purpose
- query_parameters
- request_fields
- response_fields
- error_cases

For `GET /api/hello`, you MUST document:

- method: GET
- path: /api/hello
- purpose: Retrieve a time-based greeting for the supplied user name.
- query_parameters:
  - name: string - required, non-empty
  - time: string - required, HH:mm 24-hour format
- request_fields: []
- response_fields:
  - message: string
- error_cases:
  - HTTP 400: Missing or empty name.
  - HTTP 400: Missing or invalid time.

Do not omit query_parameters, even when the endpoint uses GET.

The frontend API documentation must match the shared API contract exactly. Do not invent, rename, or omit parameters.
"""



LIST_FIELDS = [
    "pages",
    "components",
    "user_workflows",
    "api_requirements",
    "accessibility",
    "assumptions",
    "risks",
    "feedback_review",
    "open_questions",
]


def _parse_frontend_json(response: str) -> dict:
    """Parse and validate a frontend proposal."""

    response = response.strip()

    # Remove optional Markdown fences.
    if response.startswith("```"):
        lines = response.splitlines()
        lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        response = "\n".join(lines).strip()

    # Extract a possible JSON object.
    start = response.find("{")
    end = response.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError(
            "Frontend agent response contains no complete JSON object."
        )

    candidate = response[start:end + 1]

    try:
        proposal = json.loads(candidate)
    except json.JSONDecodeError as exc:
        print("\nFrontend agent returned invalid JSON.")
        print("JSON error:", exc)
        print("Response length:", len(response))
        print("Response ending:", repr(response[-300:]))

        raise ValueError(
            "Frontend agent returned malformed or incomplete JSON."
        ) from exc

   
    
    # Normalize API methods before Pydantic validates them.
    for requirement in proposal.get("api_requirements", []):
        if isinstance(requirement, dict):
            method = requirement.get("method")
            if isinstance(method, str):
                requirement["method"] = method.strip().upper()

    try:
        validated_proposal = FrontendProposal.model_validate(proposal)
    except ValidationError as exc:
        raise ValueError(
            f"Frontend proposal failed schema validation: {exc}"
        ) from exc

    result = validated_proposal.model_dump()
    result["agent"] = "Frontend Developer"
    return result




def _request_frontend_proposal(prompt: str) -> dict:
    """Request a proposal and retry once if parsing or validation fails."""

    response = ask_llm(FRONTEND_SYSTEM_PROMPT, prompt)

    try:
        return _parse_frontend_json(response)
    except ValueError:
        print("\nRetrying Frontend Agent once because its response was invalid.")

        retry_prompt = f"""
Your previous response was malformed or did not match the required schema.

Return a NEW, complete JSON object matching the system prompt exactly.
Keep the output concise. Do not add Markdown fences or explanations.

Original task:
{prompt}

Previous response:
{response[-4000:]}
"""

        retry_response = ask_llm(
            FRONTEND_SYSTEM_PROMPT,
            retry_prompt,
        )

        try:
            return _parse_frontend_json(retry_response)
        except ValueError as retry_error:
            raise ValueError(
                "Frontend Agent failed to return valid JSON after one retry."
            ) from retry_error



def propose_frontend(
    project_idea: str,
    api_contract: dict,
    technology_plan: dict,
) -> dict:
    """Generate the initial frontend proposal using the shared API contract."""

    prompt = f"""
ORIGINAL APPLICATION REQUIREMENTS:
{project_idea}
TECHNOLOGY STACK PLAN:

{json.dumps(technology_plan, indent=2)}

SHARED API CONTRACT:
{json.dumps(api_contract, separators=(",", ":"))}

Create the initial frontend design based on the original
application requirements.

For every API requirement in the shared contract, copy
the complete API specification.

This includes:
- method
- path
- purpose
- query_parameters
- request_fields
- response_fields
- error_cases

Do not omit any contract fields, even when their values
are empty arrays.

Identify the required pages, components, user workflows,
accessibility requirements, assumptions, risks and open questions.

Follow the backend API structure exactly.
TECHNOLOGY RULES:

- Follow the Technology Stack Plan.
- Do not replace explicitly requested frontend frameworks
  or programming languages.
- Use the recommended frontend technologies where appropriate.
- Do not independently select a different framework.
- Report genuine technology conflicts instead of silently
  changing the stack.

Return a concise, complete JSON proposal.
"""

    return _request_frontend_proposal(prompt)


def review_frontend(
    project_idea: str,
    own_proposal: dict,
    peer_feedback: dict,
    api_contract: dict,
    technology_plan: dict,
) -> dict:
    """Revise the frontend proposal while preserving the shared API contract."""

    prompt = f"""
APPLICATION IDEA:
{project_idea}
TECHNOLOGY STACK PLAN:

{json.dumps(technology_plan, separators=(",", ":"))}

SHARED API CONTRACT:
{json.dumps(api_contract, separators=(",", ":"))}

CURRENT FRONTEND PROPOSAL:
{json.dumps(own_proposal, separators=(",", ":"))}

PEER FEEDBACK:
{json.dumps(peer_feedback, separators=(",", ":"))}

Review and improve the existing proposal.

- Preserve every API contract field, not just method and path.
- Preserve query parameters, request fields and response fields.
- Preserve API error cases.
- Follow the backend pagination strategy.
- Implement frontend validation consistent with available
  backend validation requirements.
- Do not remove valid API requirements during revision.

Preserve the approved technology choices during revisions.
Do not change the frontend framework or programming language
without a requirement-based technical justification.
"""


    return _request_frontend_proposal(prompt)
