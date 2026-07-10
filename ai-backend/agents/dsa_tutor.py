from groq import Groq
import os
from dotenv import load_dotenv
from tools.dsa_tool import get_dsa_context, search_dsa_knowledge
from memory.memory_manager import load_memory, save_memory, add_session, format_memory_for_prompt

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_dsa_tutor(user_question: str):
    print(f"\n🎓 DSA Tutor Agent started")
    print(f"❓ Question: {user_question}")
    print("-" * 50)

    # Load memory
    memory = load_memory()
    memory_text = format_memory_for_prompt(memory)

    # RAG — search knowledge base BEFORE asking AI
    print(f"\n🔍 Searching DSA knowledge base...")
    dsa_context = get_dsa_context(user_question)
    print(f"\n📚 Found context:\n{dsa_context[:300]}...")

    # Feed context + question to AI
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=2048,
        messages=[
            {
                "role": "system",
                "content": f"""You are DevMentor AI, an expert DSA tutor.
You have been given relevant knowledge from your knowledge base.
ALWAYS use this knowledge as your primary source when answering.
Be practical, give examples in Java and Python.

Past context about this user:
{memory_text}

Knowledge base content:
{dsa_context}"""
            },
            {
                "role": "user",
                "content": user_question
            }
        ]
    )

    answer = response.choices[0].message.content
    print(f"\n✅ Answer:\n{answer}")

    # Save to memory
    memory = add_session(memory, user_question, f"Answered DSA question about: {user_question[:50]}")
    save_memory(memory)

    return answer

if __name__ == "__main__":
    run_dsa_tutor("How does binary search work and what is its time complexity?")