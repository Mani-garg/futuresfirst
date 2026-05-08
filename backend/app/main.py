from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Any
from .services import AnalyticsOrchestrator

app = FastAPI(title="Secure AI Insights Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = AnalyticsOrchestrator()

class ChatRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)
    filters: dict[str, Any] = Field(default_factory=dict)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat")
def chat(req: ChatRequest) -> dict[str, Any]:
    try:
        return orchestrator.answer(req.query, req.filters)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/dashboard")
def dashboard() -> dict[str, Any]:
    return orchestrator.dashboard_metrics()

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
