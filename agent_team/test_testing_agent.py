
from frontend_agent import propose_frontend
from backend_agent import propose_backend
from testing_agent import propose_testing


project_idea = """
Build a simple client-server web application using **Flask for the backend** and **React with TypeScript for the frontend**.

### 1. Backend Requirements – Flask

Create a REST API endpoint:

`GET /api/hello`

Accept two query parameters:
- `name` – user's name.
- `time` – user's current local time in 24-hour format (`HH:mm`).

The backend must determine the greeting based on the time received from the frontend.

Greeting rules:
- 05:00–11:59 → Good Morning
- 12:00–16:59 → Good Afternoon
- 17:00–20:59 → Good Evening
- 21:00–04:59 → Good Night

Return a JSON response.

Example:

Request:
`GET /api/hello?name=Sree&time=09:30`

Response:
```json
{
  "message": "Good Morning, Sree!"
}
```

Additional requirements:
- Validate that name and time are provided.
- Validate the time format (`HH:mm`).
- Return HTTP 400 for invalid or missing parameters.
- Implement appropriate error handling.
- Enable CORS for React-to-Flask communication.

### 2. Frontend Requirements – React + TypeScript

Create a simple, attractive and responsive UI.

Include:
- A text input box for entering the user's name.
- A Submit button.
- A response section to display the backend greeting.

When the user clicks Submit:

1. Validate that the name is not empty.
2. Get the user's current local time dynamically using JavaScript.
3. Format the time as `HH:mm` using a 24-hour clock.
4. Send both name and time to the Flask API using a GET request.
5. Display the greeting returned by the backend.
6. Display meaningful errors if the request fails.
7. Show a loading indicator while the API request is running.

Do not hardcode the time. It must be obtained dynamically whenever the user submits the form.

### 3. API Integration

The frontend must send:

`GET /api/hello?name=Sree&time=09:30`

The backend must independently determine the appropriate greeting using the received time.

Keep the API URL configurable through an environment variable.

Ensure the frontend and backend agree on:
- HTTP method.
- Endpoint path.
- Query parameter names.
- Response JSON structure.

### 4. Testing Requirements

Backend tests:
- Valid morning time.
- Valid afternoon time.
- Valid evening time.
- Valid night time.
- Missing name.
- Missing time.
- Invalid time format.

Frontend tests:
- Empty name validation.
- Correct time generation.
- API request with both parameters.
- Displaying the backend response.
- Handling API errors.

### 5. Project Structure and Documentation

Generate separate `backend` and `frontend` directories.

Include:
- Complete source code.
- Dependency files.
- Backend and frontend tests.
- `.env.example` files where required.
- README.md with installation, configuration, execution and testing instructions.

### 6. Restrictions

- Do not introduce a database.
- Do not introduce authentication.
- Do not add unrelated features.
- Keep the implementation simple and functional.
- Generate source files and documentation only.
- Do not automatically execute the generated application.
"""

api_contract = {
    "requirements": [
        {
            "method": "GET",
            "path": "/api/students",
            "purpose": "List all students",
        }
    ]
}

print("1. Asking Frontend Agent for its proposal...")
frontend = propose_frontend(project_idea, api_contract)

print("\n2. Asking Backend Agent for its proposal...")
backend = propose_backend(project_idea)

print("\n3. Asking Testing Agent to review both proposals...")
testing = propose_testing(
    project_idea,
    frontend,
    backend,
    api_contract,
)

print("\n========== TESTING AGENT PROPOSAL ==========")
print(testing)
