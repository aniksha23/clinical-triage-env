import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.env import ClinicalTriageEnv
from app.models import AskSymptomAction, OrderTestAction, FinalTriageAction
from app.tasks import TASKS

app = FastAPI(title="Clinical Triage Env")
env = ClinicalTriageEnv()


class ResetRequest(BaseModel):
    episode_id: Optional[str] = None
    seed: Optional[int] = None


class StepRequest(BaseModel):
    action_type: str
    symptom_name: Optional[str] = None
    test_name: Optional[str] = None
    urgency_level: Optional[int] = None
    care_pathway: Optional[str] = None
    critical_flags: list = Field(default_factory=list)
    confidence: Optional[float] = None
    reasoning: Optional[str] = None


@app.post("/reset")
def reset(req: ResetRequest = ResetRequest()):
    task_id = req.episode_id if req.episode_id in TASKS else "easy_triage"
    obs = env.reset(task_id)
    return obs.model_dump()


@app.post("/step")
def step(req: StepRequest):
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
            "reward": reward,  # This is now a float
            "done": done,
            "info": info,
        }
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state")
def state():
    return env.state() or {}


@app.get("/health")
def health():
    return {"status": "ok"}


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
