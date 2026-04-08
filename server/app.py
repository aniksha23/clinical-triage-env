import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import uuid
from typing import Optional, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.env import ClinicalTriageEnv
from app.models import AskSymptomAction, OrderTestAction, FinalTriageAction
from app.tasks import TASKS

app = FastAPI(title="Clinical Triage Env")

# One env instance per session — prevents concurrent requests from corrupting each other
sessions: Dict[str, ClinicalTriageEnv] = {}


class ResetRequest(BaseModel):
    episode_id: Optional[str] = None
    session_id: Optional[str] = None  # caller can pin a session, or get a new one
    seed: Optional[int] = None


class StepRequest(BaseModel):
    session_id: Optional[str] = None  # if omitted, uses most-recently-reset session
    action_type: str
    symptom_name: Optional[str] = None
    test_name: Optional[str] = None
    urgency_level: Optional[int] = None
    care_pathway: Optional[str] = None
    critical_flags: list = Field(default_factory=list)
    confidence: Optional[float] = None
    reasoning: Optional[str] = None


# Fallback for callers that don't send a session_id (e.g. simple test scripts)
_last_session_id: str = ""


@app.post("/reset")
def reset(req: ResetRequest = ResetRequest()):
    global _last_session_id
    session_id = req.session_id or str(uuid.uuid4())
    task_id = req.episode_id if req.episode_id in TASKS else "easy_triage"

    env = ClinicalTriageEnv()
    sessions[session_id] = env
    _last_session_id = session_id

    obs = env.reset(task_id)
    result = obs.model_dump()
    result["session_id"] = session_id  # return it so the caller can use it in /step
    return result


@app.post("/step")
def step(req: StepRequest):
    session_id = req.session_id or _last_session_id
    env = sessions.get(session_id)
    if env is None:
        raise HTTPException(status_code=400, detail=f"Unknown session_id '{session_id}'. Call /reset first.")

    try:
        if req.action_type == "ask_symptom":
            action = AskSymptomAction(symptom_name=req.symptom_name or "none")
        elif req.action_type == "order_test":
            action = OrderTestAction(test_name=req.test_name or "none")
        elif req.action_type == "triage":
            action = FinalTriageAction(
                urgency_level=req.urgency_level or 3,
                care_pathway=req.care_pathway or "urgent_care",
                critical_flags=req.critical_flags,
                confidence=req.confidence or 0.5,
                reasoning=req.reasoning,
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action_type: {req.action_type}")

        obs, reward, done, info = env.step(action)
        return {
            "observation": obs.model_dump(),
            "reward": reward.model_dump() if hasattr(reward, "model_dump") else reward,
            "done": done,
            "info": info,
        }
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state")
def state(session_id: Optional[str] = None):
    sid = session_id or _last_session_id
    env = sessions.get(sid)
    if env is None:
        return {}
    return env.state() or {}


@app.get("/health")
def health():
    return {"status": "ok", "active_sessions": len(sessions)}


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
