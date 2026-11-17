
import json

from llm_client import ask_llm
from pydantic import ValidationError
from schemas import BackendProposal


BACKEND_SYSTEM_PROMPT = """
You are a senior Python backend engineer on a collaborative AI team.

Your responsibility is to design the backend architecture directly
from the original application requirements.

You must define:
- Backend framework and database
- API endpoints and their HTTP methods
- Request and response fields
- Data models
- Business rules
- Validation and security requirements

The endpoints you generate will become the SHARED API CONTRACT
for the entire development team.

The Frontend Developer and Testing Engineer will use these
endpoints as the authoritative API contract.

Return exactly one complete JSON object without Markdown fences.

Required schema:
{
  "agent": "Backend Developer",
  "summary": "Short summary",
  "framework": "Framework name",
  "database": "Database name",
  "business_rules": [],
  "endpoints": [
    {
      "method": "GET",
      "path": "/api/example",
      "purpose": "Short purpose",
      "request_fields": [],
      "response_fields": [],
      "error_cases": []
    }
  ],
  "data_models": [],
  "validation_rules": [],
  "security_requirements": [],
  "assumptions": [],
  "risks": [],
  "feedback_review": [],
  "open_questions": []
}

Rules:
- Treat the original application requirements as the source of truth.
- Design endpoints that cover all required application functionality.
- Use suitable HTTP methods and consistent API paths.
- Do not assume the application is an inventory system.
- Do not introduce unrelated features.
- Maximum 5 business rules and validation rules.
- Maximum 2 error cases per endpoint.
- Maximum 3 items in risks, assumptions, feedback_review,
  open_questions, and security_requirements.
- Keep descriptions concise.
- Use arrays for collection fields.
- All list fields except endpoints and data_models must contain strings.
- data_models must contain objects with "name" and "fields".
- endpoints must contain objects with the exact endpoint fields.
- Return complete, valid JSON only.
- Do not introduce authentication mechanisms unless explicitly
  requested by the original application requirements.
- Do not require API keys, authentication headers, or authorization
  tokens without a clear requirement.
- Security requirements must be relevant to the application.
- Do not treat optional security enhancements as mandatory blockers.

During revisions:
- Preserve existing valid endpoints.
- Review frontend API requirements and QA feedback.
- Resolve genuine frontend/backend conflicts.
- Do not change valid API paths or methods without a requirement-based reason.
- Record unresolved issues honestly.

QUERY PARAMETER REQUIREMENTS:

- For search endpoints, identify the required search input
  and document it in query_parameters.
- For example, a student search endpoint may use:
  ["q: string - search term"]
- Ensure query parameters are included in the endpoint's
  API contract.
- Do not invent query parameters for endpoints that do
  not need them.

For all fields, follow the exact types defined in the required schema.
### Greeting Logic – Midnight Handling (Mandatory)

The backend must correctly handle all four greeting periods, including the night period that crosses midnight.

Use the following conditions:

- Good Morning: 05:00 <= time < 12:00
- Good Afternoon: 12:00 <= time < 17:00
- Good Evening: 17:00 <= time < 21:00
- Good Night: time >= 21:00 OR time < 05:00

Important:
- The Good Night condition must use OR, not AND, because the period spans midnight.
- Handle both evening hours (21:00–23:59) and early morning hours (00:00–04:59).
- Ensure that 04:59 returns Good Night and 05:00 returns Good Morning.
- Explicitly document this midnight-crossing condition in the backend design proposal.
- Include test scenarios for 21:00, 23:59, 00:00, 04:59 and 05:00.

### CORS Configuration – Mandatory

Configure Flask-CORS explicitly with the following two allowed origins:

- http://localhost:8081
- http://127.0.0.1:8081

Both origins must be included in the actual backend CORS configuration.

Do not use vague descriptions such as "allow localhost development origins".

The backend design proposal must explicitly list both origins.

Ensure that requests from both frontend origins are permitted to access the backend API.
"""


LIST_FIELDS = [
    "business_rules",
    "endpoints",
    "data_models",
    "validation_rules",
    "security_requirements",
    "assumptions",
    "risks",
    "feedback_review",
    "open_questions",
]

ENDPOINT_FIELDS = [
    "method",
    "path",
    "purpose",
    "request_fields",
    "response_fields",
    "error_cases",
]

VALID_HTTP_METHODS = {
    "GET", "POST", "PUT", "PATCH", "DELETE"
}


def _parse_proposal(response: str, error_message: str) -> dict:
    """Parse and validate an initial or revised backend proposal."""

    response = response.strip()

    # Remove optional Markdown code fences.
    if response.startswith("```"):
        lines = response.splitlines()
        lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        response = "\n".join(lines).strip()

    # Locate the JSON object without repairing malformed JSON.
    start = response.find("{")
    end = response.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError(
            f"{error_message} No complete JSON object was found."
        )

    candidate = response[start:end + 1]

    try:
        proposal = json.loads(candidate)
    except json.JSONDecodeError as exc:
        print("\nBackend agent returned invalid JSON.")
        print("JSON parsing error:", exc)
        print("Response length:", len(response))
        print("Response ending:", repr(response[-300:]))

        raise ValueError(
            f"{error_message} Check the LLM finish reason and response."
        ) from exc

    
    # Normalize endpoint methods before Pydantic validation.
    if isinstance(proposal, dict):
        endpoints = proposal.get("endpoints", [])

        if isinstance(endpoints, list):
            for endpoint in endpoints:
                if isinstance(endpoint, dict):
                    method = endpoint.get("method")

                    if isinstance(method, str):
                        endpoint["method"] = method.strip().upper()

    try:
        validated_proposal = BackendProposal.model_validate(proposal)
    except ValidationError as exc:
        raise ValueError(
            f"{error_message} Backend schema validation failed: {exc}"
        ) from exc

    result = validated_proposal.model_dump()
    result["agent"] = "Backend Developer"

    return result



def _request_backend_proposal(prompt: str) -> dict:
    """Request a backend proposal and retry once if invalid."""

    response = ask_llm(BACKEND_SYSTEM_PROMPT, prompt)

    try:
        return _parse_proposal(
            response,
            "Backend agent returned invalid proposal JSON.",
        )
    except ValueError as first_error:
        
        retry_prompt = f"""
Your previous response failed JSON or schema validation.

EXACT VALIDATION ERROR:
{first_error}

Return a NEW, complete JSON object following the system schema exactly.

Important:
- feedback_review must be a list of plain strings.
- open_questions must be a list of plain strings.
- risks must be a list of plain strings.
- assumptions must be a list of plain strings.
- business_rules must be a list of plain strings.
- validation_rules must be a list of plain strings.
- security_requirements must be a list of plain strings.
- data_models must be a list of objects with "name" and "fields".
- endpoints must be a list of objects matching the required schema.
- Do not put dictionaries inside lists that require strings.
- Do not include Markdown fences or explanatory text.

Original task:
{prompt}

Previous response:
{response[-3000:]}
"""


        retry_response = ask_llm(
            BACKEND_SYSTEM_PROMPT,
            retry_prompt,
        )

        try:
            return _parse_proposal(
                retry_response,
                "Backend agent returned invalid retry JSON.",
            )
        except ValueError as retry_error:
            print("\nBackend retry failed. Actual reason:")
            print(retry_error)

            raise ValueError(
                "Backend Agent failed to return a valid proposal "
                "after one retry. See the error above."
            ) from retry_error


def propose_backend(
    project_idea: str,
    technology_plan: dict
) -> dict:
    """Generate the initial backend proposal from the original requirements."""

    prompt = f"""
ORIGINAL APPLICATION REQUIREMENTS:
{project_idea}
TECHNOLOGY STACK PLAN:

{json.dumps(technology_plan, indent=2)}

Design the complete backend architecture for this application.

Choose a suitable framework and database.

Define the necessary:
- API endpoints with HTTP methods and paths
- Request and response fields
- Data models
- Business rules
- Validation rules
- Security requirements

IMPORTANT:
1. Cover all functionality requested by the user.
2. The endpoints you generate will become the shared API contract.
3. Ensure endpoint paths and HTTP methods are consistent.
4. Keep descriptions concise.
5. Do not assume requirements that the user did not specify.
6. Return the complete JSON object following the system schema.

TECHNOLOGY SELECTION RULES:

1. Follow the technology stack plan.
2. Do not replace user-specified technologies.
3. Use recommended technologies unless they conflict with
   the original requirements.
4. Do not independently introduce another framework or database.
5. If a technology choice creates a genuine technical conflict,
   explain it in assumptions or open_questions.
"""

    return _request_backend_proposal(prompt)



def review_backend(
    project_idea: str,
    own_proposal: dict,
    peer_feedback: dict,
    api_contract: dict,
    technology_plan: dict,
) -> dict:
    """Revise the backend proposal while preserving the shared API contract."""

    prompt = f"""
APPLICATION IDEA:
{project_idea}
TECHNOLOGY STACK PLAN:

{json.dumps(technology_plan, separators=(",", ":"))}

SHARED API CONTRACT (AUTHORITATIVE):
{json.dumps(api_contract, separators=(",", ":"))}

CURRENT BACKEND PROPOSAL:
{json.dumps(own_proposal, separators=(",", ":"))}

FRONTEND AND QA FEEDBACK:
{json.dumps(peer_feedback, separators=(",", ":"))}

Review the feedback critically.
Resolve genuine API path, HTTP method, field-name, validation,
business-rule, and testing conflicts where possible.

Preserve every mandatory endpoint from the shared API contract.
Keep required methods and paths unchanged.
Resolve supplied API conflicts where possible.
Record unresolved disagreements in feedback_review
and unanswered requirements in open_questions.
Do not remove valid endpoints merely to shorten the proposal.

Preserve the approved technology stack during revisions.
Do not change frameworks, languages or databases without
a requirement-based technical justification.

Return the complete revised JSON proposal.
"""

    return _request_backend_proposal(prompt)

