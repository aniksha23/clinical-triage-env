import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import uuid
from typing import Optional, Dict, List, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.queue_env import ClinicalQueueEnv
from app.models import AskSymptomAction, OrderTestAction, FinalTriageAction, TriageQueueAction, TriageQueueItem

app = FastAPI(title="Clinical Queue Env")

# One env instance per session
sessions: Dict[str, ClinicalQueueEnv] = {}


class ResetRequest(BaseModel):
    episode_id: Optional[str] = None
    session_id: Optional[str] = None  # caller can pin a session, or get a new one
    seed: Optional[int] = None


class StepRequest(BaseModel):
    session_id: Optional[str] = None  # if omitted, uses most-recently-reset session
    action_type: str
    patient_id: Optional[str] = None
    symptom_name: Optional[str] = None
    test_name: Optional[str] = None
    urgency_level: Optional[int] = None
    care_pathway: Optional[str] = None
    critical_flags: list = Field(default_factory=list)
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    queue: Optional[List[Dict[str, Any]]] = None


# Fallback for callers that don't send a session_id
_last_session_id: str = ""


@app.post("/reset")
def reset(req: ResetRequest = ResetRequest()):
    global _last_session_id
    session_id = req.session_id or str(uuid.uuid4())

    env = ClinicalQueueEnv()
    sessions[session_id] = env
    _last_session_id = session_id

    obs = env.reset()
    result = obs.model_dump()
    result["session_id"] = session_id  # return it so the caller can use it in /step
    return result


@app.post("/step")
def step(req: StepRequest):
    session_id = req.session_id or _last_session_id
    env = sessions.get(session_id)
    if env is None:
        raise HTTPException(status_code=400, detail=f"Unknown session_id '{session_id}'. Call /reset first.")

    # Fallback to active patient if not specified
    target_patient = req.patient_id or env.active_patient_id
    if target_patient and hasattr(env, "patients") and target_patient in env.patients:
        env.active_patient_id = target_patient

    try:
        if req.action_type == "ask_symptom":
            action = AskSymptomAction(patient_id=target_patient, symptom_name=req.symptom_name or "none")
        elif req.action_type == "order_test":
            action = OrderTestAction(patient_id=target_patient, test_name=req.test_name or "none")
        elif req.action_type == "triage":
            action = FinalTriageAction(
                urgency_level=req.urgency_level or 3,
                care_pathway=req.care_pathway or "urgent_care",
                critical_flags=req.critical_flags,
                confidence=req.confidence or 0.5,
                reasoning=req.reasoning,
            )
        elif req.action_type == "submit_triage_queue":
            queue_items = []
            if req.queue:
                for item in req.queue:
                    queue_items.append(TriageQueueItem(**item))
            action = TriageQueueAction(queue=queue_items)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action_type: {req.action_type}")

        obs, reward, done, info = env.step(action)
        
        # RL frameworks expect a dict with a "total" key for rewards
        if isinstance(reward, (float, int)):
            reward_data = {"total": float(reward)}
        else:
            reward_data = reward.model_dump() if hasattr(reward, "model_dump") else reward
            
        return {
            "observation": obs.model_dump() if hasattr(obs, "model_dump") else obs,
            "reward": reward_data,
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
    if hasattr(env, "state"):
        return env.state() or {}
    return env._get_obs().model_dump()


@app.get("/health")
def health():
    return {"status": "ok", "active_sessions": len(sessions)}


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
