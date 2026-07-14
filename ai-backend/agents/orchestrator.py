from groq import Groq
import os
from dotenv import load_dotenv
from agents.react_agent import run_agent
from agents.planner_agent import run_planner
from agents.dsa_tutor import run_dsa_tutor

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- Step 1: Router --- decides which agent(s) should handle the request
def route_request(user_input: str) -> dict:
    print(f"\n🧭 Orchestrator analyzing request...")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=256,
        messages=[
            {
                "role": "system",
                "content": """You are a routing agent. Decide which specialist agent should handle the user's request.

Available agents:
1. "code_reviewer" - reviews GitHub repositories and code quality
2. "planner" - creates step-by-step learning plans/roadmaps for a goal
3. "dsa_tutor" - answers specific DSA (Data Structures & Algorithms) questions

Respond in EXACT JSON format only, nothing else:
{"agent": "code_reviewer" | "planner" | "dsa_tutor", "reason": "short reason"}"""
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    raw = response.choices[0].message.content
    print(f"🗺️ Routing decision: {raw}")

    try:
        clean = raw.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        import json
        decision = json.loads(clean)
        return decision
    except Exception as e:
        print(f"⚠️ Could not parse routing decision: {e}")
        return {"agent": "dsa_tutor", "reason": "default fallback"}


# --- Step 2: Orchestrator --- calls the right agent based on routing decision
def run_orchestrator(user_input: str):
    print(f"\n🚀 Starting Orchestrator")
    print(f"📥 User request: {user_input}")
    print("=" * 50)

    decision = route_request(user_input)
    agent_choice = decision.get("agent", "dsa_tutor")
    reason = decision.get("reason", "")

    print(f"\n✅ Selected agent: {agent_choice}")
    print(f"💡 Reason: {reason}")
    print("-" * 50)

    if agent_choice == "code_reviewer":
        result = run_agent(user_input)
    elif agent_choice == "planner":
        result = run_planner(user_input)
    elif agent_choice == "dsa_tutor":
        result = run_dsa_tutor(user_input)
    else:
        print("⚠️ Unknown agent choice, defaulting to DSA tutor")
        result = run_dsa_tutor(user_input)

    return result


if __name__ == "__main__":
    run_orchestrator("I want to learn dynamic programming step by step with practice")