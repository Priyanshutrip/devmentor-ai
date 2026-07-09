import requests
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_user_repos():
    """Fetch all public repos of the user"""
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
    response = requests.get(url, headers=HEADERS)
    repos = response.json()
    return [{"name": r["name"], "url": r["html_url"], "language": r["language"]} for r in repos]

def get_repo_files(repo_name):
    """Fetch all files in a repo"""
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/contents"
    response = requests.get(url, headers=HEADERS)
    files = response.json()
    if isinstance(files, list):
        return [{"name": f["name"], "path": f["path"], "type": f["type"]} for f in files]
    return []

def get_file_content(repo_name, file_path):
    """Fetch content of a specific file"""
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/contents/{file_path}"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    if "content" in data:
        import base64
        content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
        return content
    return "Could not fetch file content"