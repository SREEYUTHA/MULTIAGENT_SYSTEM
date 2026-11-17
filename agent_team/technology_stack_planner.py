
import json
import re

from llm_client import ask_llm
from schemas import (
    TechnologyChoice,
    TechnologyStackPlan,
    ExplicitTechnologyRequirements,
)


# Known technology names and common aliases.
# This list can be extended as we add framework support.

FRONTEND_TECHNOLOGIES = {
    "vue.js": ("Vue.js", "JavaScript"),
    "vue": ("Vue.js", "JavaScript"),
    "react": ("React", "JavaScript"),
    "angular": ("Angular", "TypeScript"),
    "svelte": ("Svelte", "JavaScript"),
    "next.js": ("Next.js", "JavaScript"),
    "nextjs": ("Next.js", "JavaScript"),
    "html": ("HTML", "HTML"),
    "vanilla javascript": ("HTML + Vanilla JavaScript", "JavaScript"),
}

BACKEND_TECHNOLOGIES = {
    "fastapi": ("FastAPI", "Python"),
    "flask": ("Flask", "Python"),
    "django": ("Django", "Python"),
    "express.js": ("Express.js", "JavaScript"),
    "express": ("Express.js", "JavaScript"),
    "spring boot": ("Spring Boot", "Java"),
    "asp.net": ("ASP.NET", "C#"),
    "laravel": ("Laravel", "PHP"),
    "nestjs": ("NestJS", "TypeScript"),
}

DATABASE_TECHNOLOGIES = {
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "sqlite": "SQLite",
    "redis": "Redis",
}


TECHNOLOGY_PLANNER_SYSTEM_PROMPT = """
You are a senior software architect responsible for understanding
project requirements and planning a suitable technology stack.

Your goal is to produce a flexible, cost-effective and practical
technology stack for any type of software project.

Do not restrict your understanding to predefined frameworks,
programming languages, databases or technology categories.

==================================================
1. REQUIREMENT UNDERSTANDING
==================================================

Analyse the complete project description.

Identify:
- Technologies explicitly requested by the user.
- Programming languages and versions explicitly requested.
- Frameworks, libraries and tools explicitly requested.
- Database and infrastructure requirements.
- Technical constraints and preferences.
- Components that are unspecified.
- Ambiguities and conflicting requirements.

Preserve unfamiliar and custom technology names exactly as
the user specifies them.

==================================================
2. EXPLICIT TECHNOLOGY EXTRACTION
==================================================

Record every explicitly requested technology inside:

explicit_requirements.technologies

For every explicit technology:
- selection_source = "user_specified"
- recommendation_type = "essential"
- Preserve its name, category, version and language.
- Explain why it is included.

Do not classify your own recommendations as user specified.

==================================================
3. TECHNOLOGY RECOMMENDATIONS
==================================================

Recommend technologies only where the user has not specified
a choice and where a recommendation provides genuine value.

Use these classifications:

essential:
Required to implement the requested functionality.

recommended:
Provides a clear practical benefit.

optional:
Useful in certain situations but not necessary.

Every AI-selected technology must use:
selection_source = "recommended"

Avoid unnecessary dependencies and over-engineering.

Prefer built-in framework capabilities when appropriate.

Do not automatically recommend:
- Deployment tools
- CI/CD tools
- Docker
- Authentication libraries
- Monitoring tools
- Additional frameworks

Recommend them only when justified by the requirements.

==================================================
4. PROGRAMMING LANGUAGE RULES
==================================================

Preserve explicitly requested programming languages.

Examples:
- Vue.js with TypeScript means TypeScript.
- React with TypeScript means TypeScript.
- Flask with Python means Python.
- Django with Python means Python.

Never replace an explicit language with a framework default.

If the language is unspecified, recommend a suitable language
and explain the reason.

==================================================
5. DATABASE RULES
==================================================

database_requirement must be exactly one of:

- required
- not_required
- unspecified

If the user explicitly says no database is required,
use not_required.

Never use "none" as database_requirement.

Do not recommend a database when the user explicitly excludes it.

==================================================
6. CONSISTENCY AND CLARIFICATION
==================================================

Every explicitly requested technology must also appear in
the final technologies list.

Do not silently substitute explicit technologies.

Avoid duplicate technology entries.

If requirements conflict or important information is missing,
include clarification_questions.

Use status:
- ready
- needs_clarification

==================================================
7. REQUIRED JSON OUTPUT
==================================================

Return ONLY valid JSON using this exact structure:

{
    "technologies": [
        {
            "name": "Technology name",
            "category": "Technology category",
            "version": null,
            "language": null,
            "selection_source": "recommended",
            "recommendation_type": "essential",
            "reason": "Reason for selecting this technology."
        }
    ],
    "explicit_requirements": {
        "technologies": [],
        "constraints": [],
        "database_requirement": "unspecified"
    },
    "assumptions": [],
    "clarification_questions": [],
    "status": "ready"
}

Every technology object must contain all seven fields:
name, category, version, language, selection_source,
recommendation_type and reason.

Use empty lists when there are no entries.

Do not return old fields such as:
frontend, backend, database or additional_technologies
at the top level.

Do not return Markdown code fences.
Do not include explanations outside the JSON.
Do not invent technology versions.
"""


def find_explicit_technology(text: str, technologies: dict):
    """Find an explicitly mentioned technology from a known alias list."""

    text = text.lower()

    for alias, details in technologies.items():
        pattern = r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])"

        if re.search(pattern, text):
            if isinstance(details, tuple):
                return details[0], details[1]

            return details, None

    return None

"""
def extract_explicit_requirements(
    project_idea: str,
) -> ExplicitTechnologyRequirements:
    frontend = find_explicit_technology(
        project_idea, FRONTEND_TECHNOLOGIES
    )

    backend = find_explicit_technology(
        project_idea, BACKEND_TECHNOLOGIES
    )

    database = find_explicit_technology(
        project_idea, DATABASE_TECHNOLOGIES
    )

    lower_idea = project_idea.lower()

    no_database_phrases = [
        "no database",
        "database is not required",
        "database is not needed",
        "without a database",
        "does not require a database",
    ]

    database_required_phrases = [
        "database is required",
        "database is needed",
        "must use a database",
    ]

    if database:
        database_requirement = "required"
    elif any(
        phrase in lower_idea for phrase in no_database_phrases
    ):
        database_requirement = "not_required"
    elif any(
        phrase in lower_idea for phrase in database_required_phrases
    ):
        database_requirement = "required"
    else:
        database_requirement = "unspecified"

    return ExplicitTechnologyRequirements(
        frontend=frontend[0] if frontend else None,
        backend=backend[0] if backend else None,
        database=database[0] if database else None,
        database_requirement=database_requirement,
    )

"""
def parse_json_response(response: str) -> dict:
    """Extract a JSON object from the LLM response."""

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
        raise ValueError("Technology planner returned no valid JSON object.")

    return json.loads(response[start:end + 1])



def enforce_explicit_requirements(
    plan: TechnologyStackPlan,
    explicit: ExplicitTechnologyRequirements,
) -> TechnologyStackPlan:
    """Ensure the final plan preserves explicit user choices."""

    updates = {}

    if explicit.frontend:
        frontend_details = find_explicit_technology(
            explicit.frontend, FRONTEND_TECHNOLOGIES
        )

        updates["frontend"] = TechnologyChoice(
            name=explicit.frontend,
            language=frontend_details[1] if frontend_details else None,
            selection_source="user_specified",
            recommendation_type="essential",
            reason="Explicitly requested by the user.",
        )

    if explicit.backend:
        backend_details = find_explicit_technology(
            explicit.backend, BACKEND_TECHNOLOGIES
        )

        updates["backend"] = TechnologyChoice(
            name=explicit.backend,
            language=backend_details[1] if backend_details else None,
            selection_source="user_specified",
            recommendation_type="essential",
            reason="Explicitly requested by the user.",
        )

    if explicit.database:
        updates["database"] = TechnologyChoice(
            name=explicit.database,
            selection_source="user_specified",
            recommendation_type="essential",
            reason="Explicitly requested by the user.",
        )

    elif explicit.database_requirement == "not_required":
        updates["database"] = None

    updates["explicit_requirements"] = explicit

    return plan.model_copy(update=updates)


def validate_explicit_requirements(
    plan: TechnologyStackPlan
) -> TechnologyStackPlan:

    final_technologies = list(plan.technologies)

    for explicit in plan.explicit_requirements.technologies:

        if explicit.selection_source != "user_specified":
            raise ValueError(
                f"Explicit technology '{explicit.name}' "
                "must have selection_source='user_specified'."
            )

        existing = next(
            (
                tech for tech in final_technologies
                if tech.name.casefold().strip()
                == explicit.name.casefold().strip()
            ),
            None
        )

        if existing is None:
            final_technologies.append(explicit)

        elif existing != explicit:
            final_technologies.remove(existing)
            final_technologies.append(explicit)

    names = [
        tech.name.casefold().strip()
        for tech in final_technologies
    ]

    if len(names) != len(set(names)):
        raise ValueError("Duplicate technologies found in the stack.")

    return plan.model_copy(
        update={"technologies": final_technologies}
    )

def normalize_explicit_technologies(parsed_response: dict) -> dict:
    """Convert string technology names into TechnologyChoice objects."""

    technologies = parsed_response.get("technologies", [])

    explicit = parsed_response.get(
        "explicit_requirements", {}
    )

    explicit_technologies = explicit.get("technologies", [])

    technology_lookup = {
        item["name"].casefold(): item
        for item in technologies
        if isinstance(item, dict) and item.get("name")
    }

    normalized = []

    for item in explicit_technologies:

        if isinstance(item, dict):
            normalized.append(item)
            continue

        if isinstance(item, str):
            matched = technology_lookup.get(item.casefold())

            if matched:
                normalized.append({
                    **matched,
                    "selection_source": "user_specified",
                    "recommendation_type": "essential",
                })
            else:
                raise ValueError(
                    f"Explicit technology '{item}' "
                    "is missing from the main technologies list."
                )

    explicit["technologies"] = normalized

    return parsed_response

def plan_technology_stack(
    project_idea: str,
) -> TechnologyStackPlan:
    """
    Understand project requirements and generate a technology
    stack using one LLM call.
    """

    if not project_idea or not project_idea.strip():
        raise ValueError("Project idea cannot be empty.")

    try:
        # Step 1: Send the complete project idea to the LLM.
        response = ask_llm(
            system_prompt=TECHNOLOGY_PLANNER_SYSTEM_PROMPT,
            user_prompt=f"""
Analyse the following project requirements.

Identify explicitly requested technologies,
technical constraints and unspecified components.

Recommend technologies only where necessary.

PROJECT REQUIREMENTS:

{project_idea}

Return the complete technology stack using the required JSON structure.
""",
        )

        # Step 2: Parse the LLM response.
        parsed_response = parse_json_response(response)

        parsed_response = normalize_explicit_technologies(
            parsed_response
        )

        print("\n========== RAW LLM JSON RESPONSE ==========")
        print(json.dumps(parsed_response, indent=4))

        # Step 3: Validate the response using Pydantic.
        plan = TechnologyStackPlan.model_validate(parsed_response)

        # Step 4: Enforce explicit user requirements.
        plan = validate_explicit_requirements(plan)

    except Exception as exc:
        raise ValueError(
            f"Technology stack planning failed: {exc}"
        ) from exc

    print("\n=== TECHNOLOGY STACK PLAN ===")
    print(plan.model_dump_json(indent=2))

    return plan



