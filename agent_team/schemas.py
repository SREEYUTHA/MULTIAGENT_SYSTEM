
from typing import Literal


from pydantic import BaseModel, ConfigDict, Field, field_validator


# Shared rules for our API requirements and endpoints.
class APIBase(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)



# Technology stack planning schemas


# Technology stack planning schemas



class TechnologyChoice(APIBase):
    """Represents one technology selected for the project."""

    name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    version: str | None = None
    language: str | None = None

    selection_source: Literal[
        "user_specified",
        "recommended"
    ]

    recommendation_type: Literal[
        "essential",
        "recommended",
        "optional"
    ]

    reason: str = Field(min_length=1)


class ExplicitTechnologyRequirements(APIBase):
    """Technologies and constraints explicitly requested by the user."""

    technologies: list[TechnologyChoice] = Field(
        default_factory=list
    )

    constraints: list[str] = Field(
        default_factory=list
    )

    database_requirement: Literal[
        "required",
        "not_required",
        "unspecified"
    ] = "unspecified"


class TechnologyStackPlan(APIBase):
    """Complete technology stack identified for a project."""

    technologies: list[TechnologyChoice] = Field(
        default_factory=list
    )

    explicit_requirements: ExplicitTechnologyRequirements

    assumptions: list[str] = Field(default_factory=list)

    clarification_questions: list[str] = Field(
        default_factory=list
    )

    status: Literal[
        "ready",
        "needs_clarification"
    ]



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
    """A backend endpoint with additional error handling details."""
    pass

    # error_cases: list[str] = Field(
    #     default_factory=list,
    #     max_length=2,
    # )

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


class TestingProposal(APIBase):
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


# for code generation output validation
from pathlib import PurePosixPath


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

class FileManifestItem(APIBase):
    """Describes one file required by the application."""

    path: str = Field(min_length=1)
    purpose: str = Field(min_length=1)


class FileManifest(APIBase):
    """List of files required for the generated application."""

    files: list[FileManifestItem] = Field(min_length=1)
    
class CodeGenerationOutput(APIBase):
    """Collection of generated application files."""

    files: list[GeneratedFile] = Field(min_length=1)
