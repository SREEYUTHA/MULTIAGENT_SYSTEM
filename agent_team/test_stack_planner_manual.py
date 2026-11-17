
from technology_stack_planner import plan_technology_stack

idea = """
Build a simple client-server calculator.

Frontend: Vue.js with TypeScript.
Backend: Flask with Python.
Database: Not required.

"""

plan = plan_technology_stack(idea)


print("\n========== PLANNER RESULT ==========")

print("\nTECHNOLOGIES:")

for tech in plan.technologies:
    print(f"\nName: {tech.name}")
    print(f"Category: {tech.category}")
    print(f"Language: {tech.language}")
    print(f"Selection source: {tech.selection_source}")
    print(f"Recommendation: {tech.recommendation_type}")
    print(f"Reason: {tech.reason}")

print("\nEXPLICIT REQUIREMENTS:")

for tech in plan.explicit_requirements.technologies:
    print(f"- {tech.name} ({tech.category})")

print("\nConstraints:", plan.explicit_requirements.constraints)

print(
    "\nDatabase requirement:",
    plan.explicit_requirements.database_requirement
)

print("\nAssumptions:", plan.assumptions)
print("\nClarification questions:", plan.clarification_questions)
print("\nStatus:", plan.status)

