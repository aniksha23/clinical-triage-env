import random
from app.data import CASES
from app.tasks import TASKS
from app.models import PatientObservation
from app.grader import compute_reward


class ClinicalTriageEnv:
    def __init__(self):
        self.current_case = None

    def reset(self, task_id: str):
        case_ids = TASKS[task_id]
        case = random.choice([c for c in CASES if c["id"] in case_ids])
        self.current_case = case

        return PatientObservation(
            patient_id=case["id"],
            age=case["age"],
            symptoms=case["symptoms"],
            vitals=case["vitals"],
            history=case["history"],
            presenting_complaint=case["presenting_complaint"],
            data_completeness=case["completeness"]
        )

    def step(self, action):
        gold = self.current_case["gold"]
        reward = compute_reward(action, gold)

        return (
            PatientObservation(**self._obs_dict()),
            reward,
            True,
            {}
        )

    def state(self):
        return self.current_case

    def _obs_dict(self):
        c = self.current_case
        return {
            "patient_id": c["id"],
            "age": c["age"],
            "symptoms": c["symptoms"],
            "vitals": c["vitals"],
            "history": c["history"],
            "presenting_complaint": c["presenting_complaint"],
            "data_completeness": c["completeness"]
        }