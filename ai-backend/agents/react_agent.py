from groq import Groq
import json
import os
from dotenv import load_dotenv
from tools.github_tool import get_user_repos, get_repo_files, get_file_content
from memory.memory_manager import load_memory, save_memory, add_session, add_repo_insight, format_memory_for_prompt

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TOOLS = [
    {
        "name": "get_user_repos",
        "description": "Fetches all GitHub repositories of the user",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_repo_files",
        "description": "Fetches all files inside a specific GitHub repository",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository"
                }
            },
            "required": ["repo_name"]
        }
    },
    {
        "name": "get_file_content",
        "description": "Fetches the actual code content of a specific file in a repo",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "The name of the repository"
                },
                "file_path": {
                    "type": "string",
                    "description": "The path of the file inside the repository"
                }
            },
            "required": ["repo_name", "file_path"]
        }
    }
]

def execute_tool(tool_name, tool_input):
    print(f"\n🔧 Agent is using tool: {tool_name} with input: {tool_input}")
    if tool_name == "get_user_repos":
        return get_user_repos()
    elif tool_name == "get_repo_files":
        return get_repo_files(tool_input["repo_name"])
    elif tool_name == "get_file_content":
        return get_file_content(tool_input["repo_name"], tool_input["file_path"])
    else:
        return "Tool not found"

def run_agent(user_task):
    print(f"\n🚀 Starting ReAct Agent")
    print(f"📋 Task: {user_task}")
    print("-" * 50)

    # --- Phase 2: Load memory ---
    memory = load_memory()
    memory_text = format_memory_for_prompt(memory)
    print(f"\n🧠 Memory loaded:\n{memory_text}")

    messages = [
        {"role": "system", "content": f"""You are DevMentor AI, an intelligent coding mentor agent.
You have access to tools to fetch GitHub repositories and review code.

{memory_text}

When given a task:
1. THINK about what steps are needed
2. USE tools to gather information
3. OBSERVE the results
4. REPEAT until you have enough information
5. Give a detailed, helpful final response

At the end of your final answer, always include:
SUMMARY: <one sentence summary of what you did>
REPO_INSIGHT: <repo_name>|<one sentence insight about that repo>

Always explain your reasoning before using a tool."""},
        {"role": "user", "content": user_task}
    ]

    groq_tools = [{
        "type": "function",
        "function": {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["input_schema"]
        }
    } for t in TOOLS]

    final_answer = ""

    # ReAct loop
    while True:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=4096,
            messages=messages,
            tools=groq_tools
        )

        msg = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        print(f"\n🤔 Agent thinking... (finish_reason: {finish_reason})")

        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": msg.tool_calls or []
        })

        if finish_reason == "stop" or not msg.tool_calls:
            final_answer = msg.content
            print(f"\n✅ Final Answer:\n{final_answer}")
            break

        if finish_reason == "tool_calls" or msg.tool_calls:
            for tool_call in msg.tool_calls:
                tool_name = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)
                result = execute_tool(tool_name, tool_input)
                print(f"👀 Observing result: {str(result)[:200]}...")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

    # --- Phase 2: Save memory after agent finishes ---
    if final_answer:
        # Extract summary from final answer
        summary = "Reviewed GitHub repositories"
        repo_insight_name = ""
        repo_insight_text = ""

        for line in final_answer.split("\n"):
            if line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
            if line.startswith("REPO_INSIGHT:"):
                parts = line.replace("REPO_INSIGHT:", "").strip().split("|")
                if len(parts) == 2:
                    repo_insight_name = parts[0].strip()
                    repo_insight_text = parts[1].strip()

        # Save to memory
        memory = add_session(memory, user_task, summary)
        if repo_insight_name and repo_insight_text:
            memory = add_repo_insight(memory, repo_insight_name, repo_insight_text)
        save_memory(memory)
        return final_answer

if __name__ == "__main__":
    run_agent("Review my GitHub repositories and tell me which one has the best code quality and why.")