from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.react_agent import run_agent
from agents.planner_agent import run_planner
from agents.dsa_tutor import run_dsa_tutor
from agents.orchestrator import run_orchestrator

app = FastAPI(title="DevMentor AI API")

# Allow frontend (React) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request body schemas ---
class TaskRequest(BaseModel):
    message: str


# --- Endpoints ---
@app.get("/")
def root():
    return {"status": "DevMentor AI is running"}


@app.post("/review")
def review(request: TaskRequest):
    result = run_agent(request.message)
    return {"result": result}


@app.post("/plan")
def plan(request: TaskRequest):
    result = run_planner(request.message)
    return {"result": result}


@app.post("/ask")
def ask(request: TaskRequest):
    result = run_dsa_tutor(request.message)
    return {"result": result}


@app.post("/orchestrate")
def orchestrate(request: TaskRequest):
    result = run_orchestrator(request.message)
    return {"result": result}