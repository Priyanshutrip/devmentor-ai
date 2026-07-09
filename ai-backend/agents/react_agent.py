from groq import Groq
import json
import os
from dotenv import load_dotenv
from tools.github_tool import get_user_repos, get_repo_files, get_file_content

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- Define tools the agent can use ---
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

# --- Tool executor ---
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

# --- ReAct Agent loop ---
def run_agent(user_task):
    print(f"\n🚀 Starting ReAct Agent")
    print(f"📋 Task: {user_task}")
    print("-" * 50)

    messages = [
        {"role": "system", "content": """You are DevMentor AI, an intelligent coding mentor agent.
You have access to tools to fetch GitHub repositories and review code.
When given a task:
1. THINK about what steps are needed
2. USE tools to gather information
3. OBSERVE the results
4. REPEAT until you have enough information
5. Give a detailed, helpful final response

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

        # Add assistant message to history
        messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": msg.tool_calls or []})

        # If agent is done
        if finish_reason == "stop" or not msg.tool_calls:
            print(f"\n✅ Final Answer:\n{msg.content}")
            break

        # If agent wants to use tools
        if finish_reason == "tool_calls" or msg.tool_calls:
            for tool_call in msg.tool_calls:
                tool_name = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)

                result = execute_tool(tool_name, tool_input)

                print(f"👀 Observing result: {str(result)[:200]}...")

                # Feed result back to agent
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

# --- Run it ---
if __name__ == "__main__":
    run_agent("Review my GitHub repositories and tell me which one has the best code quality and why.")