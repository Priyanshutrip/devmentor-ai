from groq import Groq
import os
from dotenv import load_dotenv
from tools.dsa_tool import get_dsa_context, search_dsa_knowledge
from memory.memory_manager import load_memory, save_memory, add_session, format_memory_for_prompt

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(user_question: str, dsa_context: str, memory_text: str) -> str:
    """Generate the initial answer"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=2048,
        messages=[
            {
                "role": "system",
                "content": f"""You are DevMentor AI, an expert DSA tutor.
Use the knowledge base as your primary source. Be practical, give examples in Java and Python.

Past context: {memory_text}

Knowledge base content:
{dsa_context}"""
            },
            {"role": "user", "content": user_question}
        ]
    )
    return response.choices[0].message.content


def critique_answer(user_question: str, answer: str) -> dict:
    """Self-reflection step — critique the generated answer"""
    print(f"\n🪞 Agent is critiquing its own answer...")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=512,
        messages=[
            {
                "role": "system",
                "content": """You are an EXTREMELY strict reviewer, like a harsh professor grading an exam.
Find at least one thing to improve in EVERY answer — could be: missing edge case, unclear explanation, 
missing time/space complexity, no real-world example, could be more beginner-friendly, etc.
Be demanding. Only say no improvement needed if the answer is absolutely perfect and exhaustive.

Respond in EXACT JSON format only:
{"needs_improvement": true/false, "feedback": "specific issues to fix, or 'none' if answer is good"}"""
            },
            {
                "role": "user",
                "content": f"""Question: {user_question}

Answer to critique:
{answer}"""
            }
        ]
    )

    raw = response.choices[0].message.content
    print(f"📝 Critique: {raw}")

    try:
        clean = raw.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        import json
        return json.loads(clean)
    except Exception as e:
        print(f"⚠️ Could not parse critique: {e}")
        return {"needs_improvement": False, "feedback": "none"}


def improve_answer(user_question: str, original_answer: str, feedback: str, dsa_context: str) -> str:
    """Regenerate an improved answer based on critique feedback"""
    print(f"\n✨ Improving answer based on feedback...")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=2048,
        messages=[
            {
                "role": "system",
                "content": f"""You are DevMentor AI, an expert DSA tutor.
Improve the given answer based on the critique feedback provided.

Knowledge base content:
{dsa_context}"""
            },
            {
                "role": "user",
                "content": f"""Question: {user_question}

Original answer:
{original_answer}

Critique feedback to fix:
{feedback}

Provide an improved, corrected answer."""
            }
        ]
    )
    return response.choices[0].message.content


def run_dsa_tutor(user_question: str):
    print(f"\n🎓 DSA Tutor Agent started")
    print(f"❓ Question: {user_question}")
    print("-" * 50)

    memory = load_memory()
    memory_text = format_memory_for_prompt(memory)

    print(f"\n🔍 Searching DSA knowledge base...")
    dsa_context = get_dsa_context(user_question)

    # Step 1 — Generate initial answer
    print(f"\n✍️ Generating initial answer...")
    answer = generate_answer(user_question, dsa_context, memory_text)

    # Step 2 — Self-reflection: critique the answer
    critique = critique_answer(user_question, answer)

    # Step 3 — If critique says improvement needed, regenerate
    if critique.get("needs_improvement", False):
        feedback = critique.get("feedback", "")
        answer = improve_answer(user_question, answer, feedback, dsa_context)
        print(f"\n✅ Final Improved Answer:\n{answer}")
    else:
        print(f"\n✅ Final Answer (passed self-review):\n{answer}")

    memory = add_session(memory, user_question, f"Answered DSA question about: {user_question[:50]}")
    save_memory(memory)

    return answer

if __name__ == "__main__":
    run_dsa_tutor("Explain the difference between BFS and DFS with a graph that has a cycle, including edge cases")