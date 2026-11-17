
import json

from backend_agent import propose_backend


idea = (
    "Build a chicken shop inventory management system "
    "to manage chicken, fish, prawns, stock quantities, "
    "purchase prices, selling prices, and stock transactions."
)

print("Requesting backend design from Groq...")

try:
    proposal = propose_backend(idea)

    print("\n=== BACKEND AGENT PROPOSAL ===")
    print(json.dumps(proposal, indent=2))

    print("\nBackend agent completed successfully.")

except Exception as error:
    print(f"\nBackend agent failed: {error}")
