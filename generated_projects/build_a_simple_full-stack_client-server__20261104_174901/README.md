# Greeting Application

A simple full-stack client-server application that generates time-based greetings.

## Technology Stack

- **Backend:** Python Flask
- **Frontend:** React + TypeScript + Vite
- **Backend Port:** 8080
- **Frontend Port:** 8081

## Project Structure

```
.
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── tests/
│       └── test_api.py
├── frontend/
│   ├── .env.example
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── api/
│   │   │   └── hello.ts
│   │   ├── components/
│   │   │   ├── ErrorMessage.tsx
│   │   │   ├── GreetingDisplay.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── NameInput.tsx
│   │   │   └── SubmitButton.tsx
│   │   ├── styles/
│   │   │   ├── App.css
│   │   │   └── components.css
│   │   └── utils/
│   │       ├── time.ts
│   │       └── validation.ts
│   └── tests/
│       └── App.test.tsx
└── README.md
```

## API Contract

- **Method:** GET
- **Endpoint:** `/api/hello`
- **Query Parameters:**
  - `name`: string (required, non-empty)
  - `time`: string (required, `HH:mm` 24-hour format)
- **Success Response:**
  ```json
  { "message": "Good Morning, Sree!" }
  ```
- **Error Response (HTTP 400):**
  ```json
  { "error": "Missing or empty 'name' parameter." }
  ```
  ```json
  { "error": "Missing, malformed, or invalid 'time' parameter." }
  ```

## Greeting Logic

| Time Range | Greeting |
|------------|----------|
| 05:00–11:59 | Good Morning |
| 12:00–16:59 | Good Afternoon |
| 17:00–20:59 | Good Evening |
| 21:00–04:59 | Good Night |

## Setup Instructions

### 1. Install Backend Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 3. Configure Environment Variables

Copy the example environment file and adjust if needed:

```bash
cd frontend
cp .env.example .env
```

The `.env` file should contain:

```env
VITE_API_URL=http://localhost:8080
```

### 4. Start the Flask Backend

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```

The backend will run at `http://localhost:8080`.

### 5. Start the Vite Frontend

```bash
cd frontend
npm run dev
```

The frontend will run at `http://localhost:8081`.

## URLs

- **Backend:** `http://localhost:8080`
- **Frontend:** `http://localhost:8081`

## Running Tests

### Backend Tests

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
pytest tests/test_api.py -v
```

### Frontend Tests

```bash
cd frontend
npm run test
```

## CORS Configuration

The backend enables CORS for the following origins:

- `http://localhost:8081`
- `http://127.0.0.1:8081`

This ensures the React frontend can successfully communicate with the Flask backend during local development.

## Validation Rules

- **Name:** Must be present and contain at least one non-whitespace character.
- **Time:** Must match the regex `^([01]\d|2[0-3]):[0-5]\d$` (strict `HH:mm` 24-hour format).
- Additional query parameters are ignored and do not affect processing.

## Error Handling

- **HTTP 400:** Returned for missing or invalid `name` or `time` parameters.
- Error responses include meaningful messages and do not expose stack traces or internal server details.

## Accessibility

- Label elements are associated with input fields.
- The submit button is reachable via keyboard (Enter/Space).
- ARIA live regions are used for greeting and error messages.
- Sufficient color contrast is maintained for all text and UI elements.
- The layout is responsive and works with screen readers and zoom.

## Notes

- No authentication is required for the `/api/hello` endpoint.
- The frontend generates the current local time dynamically when the Submit button is clicked.
- Client-side clock drift may cause the greeting to differ from the user's expectation.
- Strict `HH:mm` validation may reject times like `5:00` (single-digit hour) even though they are logically valid.