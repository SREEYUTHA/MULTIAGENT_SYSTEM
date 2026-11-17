
import json
import re
import time

from llm_client import (
    ask_llm,
    CODEGEN_MODEL,
    CODEGEN_MAX_COMPLETION_TOKENS,
)
from schemas import (
    CodeGenerationOutput,
    FileManifest,
    GeneratedFile,
)

CODE_GENERATION_SYSTEM_PROMPT = """
You are a senior software developer responsible for generating
actual application source code.

Follow the original application requirements and approved
architecture carefully.

Rules:
- Generate usable source code, not pseudocode.
- Follow the approved frontend and backend designs.
- Implement the approved API contract exactly.
- Keep frontend and backend API paths consistent.
- Use appropriate error handling and input validation.
- Do not introduce unrelated application-specific assumptions.
- Do not use fake placeholder implementations.
- Do not include real API keys, passwords, or secrets.
- Do not claim that code has been executed or tested.

Return exactly one valid JSON object:

{
  "files": [
    {
      "path": "relative/path/to/file",
      "content": "actual file content"
    }
  ]
}

The file paths must be relative to the generated project folder.

Return valid JSON only. Do not use Markdown code fences.
"""


def _serialize(value):
    """Convert Pydantic models or dictionaries into JSON."""

    if hasattr(value, "model_dump"):
        value = value.model_dump()

    return json.dumps(value, indent=2, default=str)


def _parse_json_object(response):
    """Extract and parse a JSON object from an LLM response."""

    response = response.strip()

    response = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        response,
        flags=re.IGNORECASE,
    ).strip()

    start = response.find("{")
    end = response.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError(
            "LLM returned no complete JSON object."
        )

    return json.loads(response[start:end + 1])



def _generate_file_manifest(
    project_idea,
    api_contract,
    frontend_proposal,
    backend_proposal,
    testing_proposal,
    technology_plan,
):
    """Generate a dynamic list of required application files."""

    system_prompt = """
You are a senior software architect.

Your task is to determine the complete file structure
required to implement the approved application.

Rules:
- Derive files from the original application requirements.
- Follow the approved frontend and backend frameworks.
- Include all files necessary for the approved architecture.
- Include API routes, models, database configuration,
  business logic and validation where required.
- Include frontend entry points, pages, components,
  routing, styles and API integration where required.
- Include appropriate configuration and documentation files.
- Include README.md.
- Do not invent unrelated functionality.
- Do not include generated test files unless the testing
  plan requires them.
- Do not create duplicate file paths.
- Use relative POSIX paths.
- Return valid JSON only.

Required structure:

{
  "files": [
    {
      "path": "relative/path/to/file",
      "purpose": "Why this file is required"
    }
  ]
}
"""

    user_prompt = f"""
ORIGINAL APPLICATION REQUIREMENTS:
{project_idea}

APPROVED TECHNOLOGY STACK:
{_serialize(technology_plan)}
APPROVED API CONTRACT:
{_serialize(api_contract)}

APPROVED FRONTEND DESIGN:
{_serialize(frontend_proposal)}

APPROVED BACKEND DESIGN:
{_serialize(backend_proposal)}

TESTING PLAN:
{_serialize(testing_proposal)}

Create the complete file manifest for this application.

- Follow the approved technology stack exactly.
- Do not replace user-selected programming languages,
  frameworks, or database technologies.
- Include configuration files required by the selected stack.
- Ensure the file structure is compatible with the approved architecture.

Return every required file, with its path and purpose.
Do not generate source code yet.
"""

    response = ask_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=CODEGEN_MODEL,
        max_completion_tokens=CODEGEN_MAX_COMPLETION_TOKENS,
    )

    manifest_data = _parse_json_object(response)

    try:
        manifest = FileManifest.model_validate(manifest_data)
    except Exception as exc:
        raise ValueError(
            f"Invalid file manifest: {exc}"
        ) from exc

    paths = [item.path for item in manifest.files]

    if len(paths) != len(set(paths)):
        raise ValueError(
            "File manifest contains duplicate paths."
        )

    print("\nGenerated file manifest:")

    for item in manifest.files:
        print(f"- {item.path}: {item.purpose}")

    return manifest




def _generate_single_file(
    manifest_item,
    project_idea,
    api_contract,
    frontend_proposal,
    backend_proposal,
    testing_proposal,
    technology_plan,
    existing_paths,
):
    """Generate one source file from the approved manifest."""

    system_prompt = """
You are a senior software developer.

Generate exactly ONE complete application source file.

Rules:
- Follow the original application requirements.
- Follow the approved frontend and backend architecture.
- Implement the specified file purpose.
- Use the exact approved API contract.
- Keep imports and framework usage consistent.
- Write usable source code, not pseudocode.
- Do not generate unrelated files.
- Do not include Markdown code fences.
- Do not include real credentials or secrets.
- Do not claim that code was executed or tested.

Return exactly one JSON object:

{
  "path": "relative/path/to/file",
  "content": "complete source code"
}

Return valid JSON only.
"""

    user_prompt = f"""
ORIGINAL APPLICATION REQUIREMENTS:
{project_idea}
APPROVED TECHNOLOGY STACK:
{_serialize(technology_plan)}

APPROVED API CONTRACT:
{_serialize(api_contract)}

APPROVED FRONTEND DESIGN:
{_serialize(frontend_proposal)}

APPROVED BACKEND DESIGN:
{_serialize(backend_proposal)}

TESTING PLAN:
{_serialize(testing_proposal)}

FILE TO GENERATE:
Path: {manifest_item.path}
Purpose: {manifest_item.purpose}

ALREADY GENERATED FILE PATHS:
{json.dumps(existing_paths, indent=2)}

Generate only the requested file.

The returned path must exactly match:
{manifest_item.path}

Follow the approved technology stack exactly.
Do not replace the selected frameworks, programming languages,
or database technologies.
Return the complete file content.
"""

    response = ask_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=CODEGEN_MODEL,
        max_completion_tokens=CODEGEN_MAX_COMPLETION_TOKENS,
    )

    file_data = _parse_json_object(response)

    try:
        generated_file = GeneratedFile.model_validate(file_data)
    except Exception as exc:
        raise ValueError(
            f"Invalid generated file {manifest_item.path}: {exc}"
        ) from exc

    if generated_file.path != manifest_item.path:
        raise ValueError(
            f"Expected {manifest_item.path}, "
            f"but received {generated_file.path}."
        )

    if not generated_file.content.strip():
        raise ValueError(
            f"Generated file is empty: {manifest_item.path}"
        )

    return generated_file


def _parse_generated_files(response):
    """Parse and validate generated files."""

    response = response.strip()

    response = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        response,
        flags=re.IGNORECASE,
    ).strip()

    start = response.find("{")
    end = response.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError(
            "Code generation agent returned no complete JSON object."
        )

    candidate = response[start:end + 1]

    try:
        result = CodeGenerationOutput.model_validate_json(candidate)
    except Exception as exc:
        raise ValueError(
            f"Invalid generated file structure: {exc}"
        ) from exc

    return result.files




def generate_project_files(
    project_idea,
    api_contract,
    frontend_proposal,
    backend_proposal,
    testing_proposal,
    technology_plan,
):
    """
    Generate application files using a dynamic manifest.

    1. Create the file manifest.
    2. Generate each file individually.
    3. Validate and collect generated files.
    4. Return all files together.

    The generated application is never executed.
    """

    print("\n[Code Generation] Creating file manifest...")

    manifest = _generate_file_manifest(
        project_idea=project_idea,
        api_contract=api_contract,
        frontend_proposal=frontend_proposal,
        backend_proposal=backend_proposal,
        testing_proposal=testing_proposal,
        technology_plan=technology_plan,
    )

    
    existing_paths = set()
    generated_files = []

    total_files = len(manifest.files)

    print(
        f"\n[Code Generation] "
        f"Manifest contains {total_files} files."
    )

    for index, manifest_item in enumerate(
        manifest.files,
        start=1,
    ):

        path = manifest_item.path

        print(
            f"\nGenerating file {index}/{total_files}: {path}"
        )

        if path in existing_paths:
            raise ValueError(
                f"Duplicate path in manifest: {path}"
            )

        generated_file = _generate_single_file(
            manifest_item=manifest_item,
            project_idea=project_idea,
            api_contract=api_contract,
            frontend_proposal=frontend_proposal,
            backend_proposal=backend_proposal,
            testing_proposal=testing_proposal,
            technology_plan=technology_plan,
            existing_paths=sorted(existing_paths),
        )

        existing_paths.add(generated_file.path)
        generated_files.append(generated_file)

        print(f"[Code Generation] Completed: {path}")

    print(
        f"\n[Code Generation] Successfully generated "
        f"{len(generated_files)} files."
    )

    return CodeGenerationOutput(files=generated_files)
