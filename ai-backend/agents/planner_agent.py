from groq import Groq
import json
import os
from dotenv import load_dotenv
from memory.memory_manager import load_memory, save_memory, add_session, format_memory_for_prompt

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- Step 1: Planner --- generates subtasks from one big task
def create_plan(user_goal: str, memory_text: str) -> list:
    print(f"\n📋 Creating plan for: {user_goal}")
    print("-" * 50)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1024,
        messages=[
            {
                "role": "system",
                "content": """You are a planning agent. Your job is to break down a learning goal into clear subtasks.
Always respond in this exact JSON format and nothing else:
{
  "plan": [
    {"step": 1, "task": "...", "goal": "..."},
    {"step": 2, "task": "...", "goal": "..."},
    {"step": 3, "task": "...", "goal": "..."}
  ]
}
Maximum 4 steps. Be specific and practical."""
            },
            {
                "role": "user",
                "content": f"""Past context: {memory_text}
                
My learning goal: {user_goal}

Break this into subtasks."""
            }
        ]
    )

    raw = response.choices[0].message.content
    print(f"\n🗺️ Raw plan from AI:\n{raw}")

    # Parse JSON response
    try:
        clean = raw.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        plan_data = json.loads(clean)
        return plan_data["plan"]
    except Exception as e:
        print(f"⚠️ Could not parse plan: {e}")
        return [{"step": 1, "task": user_goal, "goal": "Complete the goal"}]


# --- Step 2: Executor --- executes each subtask one by one (this is the Chain)
def execute_step(step: dict, previous_output: str, memory_text: str) -> str:
    print(f"\n⚙️ Executing step {step['step']}: {step['task']}")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1024,
        messages=[
            {
                "role": "system",
                "content": """You are DevMentor AI, an expert coding mentor.
Execute the given subtask clearly and practically.
Give actionable output that feeds into the next step."""
            },
            {
                "role": "user",
                "content": f"""Past context: {memory_text}

Previous step output:
{previous_output if previous_output else "This is the first step."}

Current subtask: {step['task']}
Goal of this step: {step['goal']}

Execute this step now."""
            }
        ]
    )

    output = response.choices[0].message.content
    print(f"\n✅ Step {step['step']} output:\n{output[:300]}...")
    return output


# --- Main planning + chaining loop ---
def run_planner(user_goal: str):
    print(f"\n🚀 Starting Planner Agent")
    print(f"🎯 Goal: {user_goal}")
    print("=" * 50)

    # Load memory
    memory = load_memory()
    memory_text = format_memory_for_prompt(memory)
    print(f"\n🧠 Memory loaded: {memory_text[:100]}...")

    # Step 1 — Create plan
    plan = create_plan(user_goal, memory_text)
    print(f"\n📋 Plan created with {len(plan)} steps:")
    for step in plan:
        print(f"  Step {step['step']}: {step['task']}")

    # Step 2 — Execute each step (Chain!)
    previous_output = ""
    all_outputs = []

    for step in plan:
        output = execute_step(step, previous_output, memory_text)
        previous_output = output      # ← THIS IS THE CHAIN
        all_outputs.append({
            "step": step["step"],
            "task": step["task"],
            "output": output
        })

    # Step 3 — Final summary
    print("\n" + "=" * 50)
    print("🎓 COMPLETE LEARNING ROADMAP")
    print("=" * 50)
    for item in all_outputs:
        print(f"\n📌 Step {item['step']}: {item['task']}")
        print(f"{item['output']}")
        print("-" * 40)

    # Save to memory
    summary = f"Created learning plan for: {user_goal} with {len(plan)} steps"
    memory = add_session(memory, user_goal, summary)
    save_memory(memory)

    return all_outputs


if __name__ == "__main__":
    run_planner("I want to learn error handling in Java and practice DSA problems related to it")