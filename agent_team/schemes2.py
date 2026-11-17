from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pathlib import PurePosixPath

# Shared rules for our API requirements and endpoints.
class APIBase(BaseModel):
    # Change to "ignore" if the LLM occasionally adds unmapped conversational keys
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


# An API requirement proposed by the frontend agent.
class APIRequirement(APIBase):
    """An API requirement shared between frontend and backend."""

    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    path: str = Field(min_length=1, pattern=r"^/")
    purpose: str = Field(min_length=1)

    # Query parameters such as page, limit, name and course.
    query_parameters: list[str] = Field(default_factory=list)

    # Request and response fields.
    request_fields: list[str] = Field(default_factory=list)
    response_fields: list[str] = Field(default_factory=list)
    error_cases: list[str] = Field(default_factory=list, max_length=2)


class SharedAPIContract(APIBase):
    """Mandatory API requirements shared by frontend and backend agents."""

    requirements: list[APIRequirement]


# An API endpoint proposed by the backend agent.
class APIEndpoint(APIRequirement):
    """A backend endpoint inheriting all APIRequirement structures."""
    # REMOVED: Duplicated error_cases definition to avoid Pydantic field shadowing conflicts.
    # Add unique backend-only specifications here if needed (e.g., controller_method: str)
    pass


class FrontendProposal(APIBase):
    agent: str = "Frontend Developer"
    summary: str
    framework: str
    pages: list[str]
    components: list[str]
    user_workflows: list[str]
    api_requirements: list[APIRequirement]
    accessibility: list[str]
    assumptions: list[str]
    risks: list[str]
    feedback_review: list[str]
    open_questions: list[str]

    @field_validator("summary", "framework")
    @classmethod
    def must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field must not be empty.")
        return value


class DataModel(APIBase):
    name: str = Field(min_length=1)
    fields: list[str] = Field(min_length=1)


class BackendProposal(APIBase):
    agent: str = "Backend Developer"
    summary: str = Field(min_length=1)
    framework: str = Field(min_length=1)
    database: str = Field(min_length=1)

    business_rules: list[str] = Field(max_length=5)
    endpoints: list[APIEndpoint]
    data_models: list[DataModel] = Field(max_length=5)
    validation_rules: list[str] = Field(max_length=5)
    security_requirements: list[str] = Field(max_length=3)
    assumptions: list[str] = Field(max_length=3)
    risks: list[str] = Field(max_length=3)
    feedback_review: list[str] = Field(max_length=3)
    open_questions: list[str] = Field(max_length=3)


class TestScenario(APIBase):
    name: str = Field(min_length=1)
    type: str = Field(min_length=1)
    steps: list[str] = Field(min_length=1)
    expected_result: str = Field(min_length=1)


# Renamed to completely prevent pytest tracking interception issues
class AgentTestingProposal(APIBase):
    __test__ = False
    agent: str = "Testing Engineer"
    summary: str = Field(min_length=1)
    requirements_review: list[str] = Field(max_length=5)
    frontend_backend_conflicts: list[str] = Field(max_length=3)
    test_scenarios: list[TestScenario] = Field(max_length=3)
    validation_checks: list[str] = Field(max_length=3)
    security_checks: list[str] = Field(max_length=3)
    risks: list[str] = Field(max_length=3)
    feedback_review: list[str] = Field(max_length=3)
    open_questions: list[str] = Field(max_length=3)
    blockers: list[str] = Field(max_length=3)


class GeneratedFile(APIBase):
    """A single generated application file."""

    path: str = Field(min_length=1)
    content: str

    @field_validator("path")
    @classmethod
    def validate_file_path(cls, value: str) -> str:
        path = PurePosixPath(value)
        if (
            path.is_absolute()
            or "\\" in value
            or ".." in path.parts
            or ":" in value
            or not path.parts
        ):
            raise ValueError("Unsafe generated file path.")
        return value


class CodeGenerationOutput(APIBase):
    """Collection of generated application files."""

    files: list[GeneratedFile] = Field(min_length=1)
