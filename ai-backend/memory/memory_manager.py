import json
import os
from datetime import datetime

MEMORY_FILE = "memory/memory_store.json"

def load_memory():
    """Load memory from file"""
    if not os.path.exists(MEMORY_FILE):
        return {
            "sessions": [],
            "repo_insights": {},
            "user_weak_areas": [],
            "last_reviewed": None
        }
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory: dict):
    """Save memory to file"""
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)
    print(f"\n💾 Memory saved!")

def add_session(memory: dict, task: str, summary: str):
    """Add a new session to memory"""
    session = {
        "timestamp": datetime.now().isoformat(),
        "task": task,
        "summary": summary
    }
    memory["sessions"].append(session)
    memory["last_reviewed"] = datetime.now().isoformat()
    return memory

def add_repo_insight(memory: dict, repo_name: str, insight: str):
    """Store insight about a specific repo"""
    memory["repo_insights"][repo_name] = {
        "insight": insight,
        "timestamp": datetime.now().isoformat()
    }
    return memory

def format_memory_for_prompt(memory: dict) -> str:
    """Convert memory into text the AI can read"""
    if not memory["sessions"]:
        return "No previous sessions. This is the first interaction."

    lines = ["📚 Past session memory:"]

    # Last 3 sessions only
    for s in memory["sessions"][-3:]:
        lines.append(f"- [{s['timestamp'][:10]}] Task: {s['task']} → {s['summary']}")

    if memory["repo_insights"]:
        lines.append("\n🔍 Known repo insights:")
        for repo, data in memory["repo_insights"].items():
            lines.append(f"- {repo}: {data['insight']}")

    if memory["user_weak_areas"]:
        lines.append(f"\n⚠️ User weak areas: {', '.join(memory['user_weak_areas'])}")

    return "\n".join(lines)