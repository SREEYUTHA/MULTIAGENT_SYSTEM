
import json

from frontend_agent import propose_frontend


idea = (
    "Build a chicken shop inventory management system "
    "to track chicken, fish, prawns, stock quantities, "
    "purchase prices, and selling prices."
)

print("Requesting frontend design from Groq...")

try:
    proposal = propose_frontend(idea)

    print("\n=== FRONTEND AGENT PROPOSAL ===")
    print(json.dumps(proposal, indent=2))

    print("\nFrontend agent completed successfully.")

except Exception as error:
    print(f"\nFrontend agent failed: {error}")
