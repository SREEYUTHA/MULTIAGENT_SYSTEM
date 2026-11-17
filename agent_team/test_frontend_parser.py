
from frontend_agent import _parse_frontend_json

sample = {
    "summary": "Inventory interface",
    "framework": "React",
    "pages": [],
    "components": [],
    "user_workflows": [],
    "api_requirements": [
        {
            "method": "get",
            "path": "/api/products",
            "purpose": "List products"
        }
    ],
    "accessibility": [],
    "assumptions": [],
    "risks": [],
    "feedback_review": [],
    "open_questions": []
}

result = _parse_frontend_json(__import__("json").dumps(sample))

print("Parser test passed!")
print("Normalized API:", result["api_requirements"][0])
