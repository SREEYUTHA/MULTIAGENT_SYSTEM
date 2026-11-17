import json

from workflow_graph import team_graph


def display_agent(title: str, proposal: dict) -> None:
    print(f"\n{'=' * 12} {title} {'=' * 12}")
    print(json.dumps(proposal, indent=2, ensure_ascii=False))


def run_orchestrator() -> None:

    print("\n=== AI SOFTWARE DEVELOPMENT TEAM ===")

    # Define the application idea directly here.
    project_idea = """
    Build a simple **Client-Server Calculator Application**.

### Project Objective
Create a web-based calculator where users enter two numbers, select an arithmetic operation, and receive the calculated result from a Python backend server.

### Technology Preferences
- Frontend: React with TypeScript
- Backend: Python with FastAPI
- Communication: REST API using HTTP POST requests
- Styling: CSS
- No database required.

### Frontend Requirements
1. Create a clean, responsive calculator interface.
2. Provide two input fields for entering numbers.
3. Provide operation buttons for:
   - Addition (+)
   - Subtraction (-)
   - Multiplication (×)
   - Division (÷)
4. Include a Calculate action.
5. Display the calculated result received from the backend.
6. Display meaningful error messages for invalid inputs.
7. Show a loading state while waiting for the server response.

### Backend Requirements
1. Create a FastAPI server.
2. Implement a POST endpoint `/api/calculate`.
3. Accept two numbers and an arithmetic operation in JSON format.
4. Perform the requested calculation on the server.
5. Return the result in JSON format.
6. Handle division by zero.
7. Validate input values and return appropriate HTTP error responses.

### API Contract

**Request:**
```json
{
  "num1": 20,
  "num2": 10,
  "operation": "add"
}
```

**Successful response:**
```json
{
  "success": true,
  "result": 30,
  "message": "Calculation successful"
}
```

### Testing Requirements
1. Test all four arithmetic operations.
2. Test division by zero.
3. Test missing and invalid input values.
4. Verify frontend-backend API communication.
5. Verify the API response matches the agreed contract.

### Project Deliverables
- Complete frontend source code.
- Complete backend source code.
- Backend and frontend dependency files.
- README with installation and execution instructions.
- Instructions to start the frontend and backend separately.

### Important Constraints
- Keep the application beginner-friendly and maintainable.
- Do not use a database.
- Do not add authentication or unnecessary features.
- The backend must perform all calculations; do not calculate results directly in the frontend.
- Generate source files and documentation only. Do not automatically execute the generated application.
    """

    print("\nProject idea:")
    # print(project_idea)

    try:
        print("\nStarting the LangGraph workflow...")

        result = team_graph.invoke({
            "project_idea": project_idea
        })

        display_agent(
            "SHARED API CONTRACT",
            result["api_contract"],
        )

        display_agent(
            "INITIAL FRONTEND PROPOSAL",
            result["frontend"],
        )

        display_agent(
            "INITIAL BACKEND PROPOSAL",
            result["backend"],
        )

        display_agent(
            "INITIAL QA REVIEW",
            result["testing"],
        )

        display_agent(
            "REVISED FRONTEND DESIGN",
            result["revised_frontend"],
        )

        display_agent(
            "REVISED BACKEND DESIGN",
            result["revised_backend"],
        )

        display_agent(
            "FINAL QA REVIEW",
            result["final_testing"],
        )

        api_conflicts = result.get("api_conflicts", [])

        print("\n=== API CONTRACT VALIDATION ===")

        if api_conflicts:
            for conflict in api_conflicts:
                print(f"- {conflict}")
        else:
            print("No API method/path conflicts detected.")

        print("\n=== DESIGN READINESS CHECK ===")

        invalid_fields = result.get("invalid_fields", [])
        blockers = result.get("blockers", [])
        conflicts = result.get("all_conflicts", [])

        if invalid_fields:
            print("\nInvalid or missing QA fields:")
            for field in invalid_fields:
                print(f"- {field}")

        if blockers:
            print("\nBlockers:")
            for blocker in blockers:
                print(f"- {blocker}")

        if conflicts:
            print("\nFrontend/backend and API conflicts:")
            for conflict in conflicts:
                print(f"- {conflict}")

        if result.get("outcome") == "approved":

            print("\n=== APPLICATION GENERATED SUCCESSFULLY ===")
            print("The design passed QA and code generation completed.")

            project_path = result.get("generated_project_path")
            project_name = result.get("project_name")
            generated_files = result.get("generated_files", [])

            print(f"\nProject name: {project_name}")
            print(f"Project location: {project_path}")

            print(f"\nGenerated files ({len(generated_files)}):")

            for file in generated_files:
                print(f"  - {file['path']}")

            print("\nREADME.md contains setup and run instructions.")
            print("\nNote: Generated code has not been executed or tested.")

        else:

            print("\n=== DESIGN NOT APPROVED ===")
            print("Resolve the reported issues before proceeding.")
            print("No application files were generated.")

    except Exception as exc:

        print("\nThe orchestration workflow failed.")
        print(f"Error type: {type(exc).__name__}")
        print(f"Error details: {exc}")

        print(
            "\nCheck the agent response, graph state, "
            "and API contract validator."
        )


if __name__ == "__main__":
    run_orchestrator()
