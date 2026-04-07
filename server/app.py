import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from typing import Optional, Any, Dict
from pydantic import Field
from openenv.core import create_fastapi_app, Environment, Observation, Action

from app.env import ClinicalTriageEnv
from app.models import (
    PatientObservation, AskSymptomAction, OrderTestAction,
    FinalTriageAction, TriageReward
)
from app.tasks import TASKS


# --- Openenv-compatible observation (adds done/reward to PatientObservation) ---
class TriageObservation(Observation):
    patient_id: str = ""
    age: int = 0
    presenting_complaint: str = ""
    symptoms: Dict[str, bool] = Field(default_factory=dict)
    vitals: Dict[str, Any] = Field(default_factory=dict)
    history: list = Field(default_factory=list)
    available_actions: list = Field(default_factory=list)
    data_completeness: float = 0.0

    @classmethod
    def from_patient_obs(cls, obs: PatientObservation, done: bool = False, reward: float = 0.0):
        return cls(
            patient_id=obs.patient_id,
            age=obs.age,
            presenting_complaint=obs.presenting_complaint,
            symptoms=obs.symptoms,
            vitals=obs.vitals,
            history=obs.history,
            available_actions=obs.available_actions,
            data_completeness=obs.data_completeness,
            done=done,
            reward=reward,
        )


# --- Openenv-compatible action (wraps all three action types) ---
class TriageActionInput(Action):
    action_type: str
    symptom_name: Optional[str] = None
    test_name: Optional[str] = None
    urgency_level: Optional[int] = None
    care_pathway: Optional[str] = None
    critical_flags: list = Field(default_factory=list)
    confidence: Optional[float] = None
    reasoning: Optional[str] = None

    def to_env_action(self):
        if self.action_type == "ask_symptom":
            return AskSymptomAction(symptom_name=self.symptom_name or "none")
        elif self.action_type == "order_test":
            return OrderTestAction(test_name=self.test_name or "none")
        elif self.action_type == "triage":
            return FinalTriageAction(
                urgency_level=self.urgency_level or 3,
                care_pathway=self.care_pathway or "urgent_care",
                critical_flags=self.critical_flags,
                confidence=self.confidence or 0.5,
                reasoning=self.reasoning,
            )
        raise ValueError(f"Unknown action_type: {self.action_type}")


# --- Wrapper env that adapts ClinicalTriageEnv to openenv's interface ---
class ClinicalTriageEnvServer(Environment):
    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self):
        super().__init__()
        self._env = ClinicalTriageEnv()

    def reset(self, seed: Optional[int] = None, episode_id: Optional[str] = None, **kwargs) -> TriageObservation:
        task_id = episode_id if episode_id in TASKS else "easy_triage"
        obs = self._env.reset(task_id)
        return TriageObservation.from_patient_obs(obs)

    def step(self, action: TriageActionInput, timeout_s: Optional[float] = None, **kwargs) -> TriageObservation:
        env_action = action.to_env_action()
        obs, reward, done, info = self._env.step(env_action)
        return TriageObservation.from_patient_obs(obs, done=done, reward=reward.total)

    def state(self) -> Dict[str, Any]:
        return self._env.state() or {}


app = create_fastapi_app(
    env=ClinicalTriageEnvServer,
    action_cls=TriageActionInput,
    observation_cls=TriageObservation,
)


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
