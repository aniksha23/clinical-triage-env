import random
from typing import Tuple, Dict, Any

from app.data import CASES
from app.tasks import TASKS
from app.models import PatientObservation, TriageAction, TriageReward, FinalTriageAction, AskSymptomAction, OrderTestAction
from app.grader import compute_reward


class ClinicalTriageEnv:
    def __init__(self):
        self.current_case = None
        self.revealed_symptoms = {}
        self.revealed_vitals = {}
        self.cumulative_cost = 0.0
        self.is_done = False

    def reset(self, task_id: str) -> PatientObservation:
        case_ids = TASKS.get(task_id, [])
        if not case_ids:
            raise ValueError(f"Task ID {task_id} not found in TASKS.")
        
        case = random.choice([c for c in CASES if c["id"] in case_ids])
        self.current_case = case
        
        # Reset state
        self.revealed_symptoms = {}
        self.revealed_vitals = {}
        self.cumulative_cost = 0.0
        self.is_done = False
        
        # Initial reveal: Age, Complaint, and ONE random vital
        all_vitals = list(case["vitals"].keys())
        initial_vital = random.choice(all_vitals)
        self.revealed_vitals[initial_vital] = case["vitals"][initial_vital]
        
        return self._get_obs()

    def step(self, action: TriageAction) -> Tuple[PatientObservation, TriageReward, bool, Dict[str, Any]]:
        if self.is_done:
            raise RuntimeError("Episode is already done. Call reset().")

        if action.action_type == "ask_symptom":
            symptom = action.symptom_name
            # If valid symptom, reveal it (otherwise it stays hidden or null)
            if symptom in self.current_case["symptoms"]:
                self.revealed_symptoms[symptom] = True
            else:
                self.revealed_symptoms[symptom] = False
            
            self.cumulative_cost += 0.05  # Cost for asking a symptom
            reward = TriageReward(total=0.0, accuracy_score=0.0, cost_penalty=self.cumulative_cost, done=False, message=f"Asked about {symptom}")
            return self._get_obs(), reward, False, {}

        elif action.action_type == "order_test":
            test = action.test_name
            if test in self.current_case["vitals"]:
                self.revealed_vitals[test] = self.current_case["vitals"][test]
            
            self.cumulative_cost += 0.1  # Cost for ordering a test
            reward = TriageReward(total=0.0, accuracy_score=0.0, cost_penalty=self.cumulative_cost, done=False, message=f"Ordered test: {test}")
            return self._get_obs(), reward, False, {}

        elif action.action_type == "triage":
            reward = compute_reward(action, self.current_case["gold"], self.cumulative_cost)
            self.is_done = True
            return self._get_obs(), reward, True, {}

        else:
            raise ValueError(f"Unknown action type: {action.action_type}")

    def state(self) -> Dict[str, Any]:
        """Returns the full ground truth case data."""
        return self.current_case

    def _get_obs(self) -> PatientObservation:
        c = self.current_case
        return PatientObservation(
            patient_id=c["id"],
            age=c["age"],
            presenting_complaint=c["presenting_complaint"],
            symptoms=self.revealed_symptoms,
            vitals=self.revealed_vitals,
            history=[], # History starts hidden
            available_actions=self._get_available_actions(),
            data_completeness=c["completeness"]
        )

    def _get_available_actions(self) -> list:
        # Potential symptoms and tests the agent could ask for
        possible_symptoms = ["chest_pain", "shortness_of_breath", "fever", "cough", "nausea", "dizziness", "confusion"]
        possible_tests = ["bp", "hr", "temp", "spo2"]
        
        actions = [f"ask_symptom({s})" for s in possible_symptoms if s not in self.revealed_symptoms]
        actions += [f"order_test({t})" for t in possible_tests if t not in self.revealed_vitals]
        actions += ["triage"]
        return actions