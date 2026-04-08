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

    def reset(self, task_id: str, case_id: str = None) -> PatientObservation:
        case_ids = TASKS.get(task_id, [])
        if not case_ids:
            raise ValueError(f"Task ID {task_id} not found in TASKS.")

        if case_id:
            case = next((c for c in CASES if c["id"] == case_id), None)
            if case is None:
                raise ValueError(f"Case ID {case_id} not found in CASES.")
        else:
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

    def step(self, action: TriageAction) -> Tuple[PatientObservation, float, bool, Dict[str, Any]]:
        if self.is_done:
            raise RuntimeError("Episode is already done. Call reset().")

        if action.action_type == "ask_symptom":
            symptom = action.symptom_name

            # Duplicate ask: still charge cost, but no info gain
            if symptom in self.revealed_symptoms:
                self.cumulative_cost += 0.05
                step_reward = 0.001
                reward = TriageReward(total=step_reward, accuracy_score=0.005, cost_penalty=max(0.005, min(0.995, self.cumulative_cost)), done=False, message=f"Already asked about {symptom}")
                return self._get_obs(), reward.total, False, {"grader_score": step_reward, "detailed_reward": reward.model_dump()}

            if symptom in self.current_case["symptoms"]:
                self.revealed_symptoms[symptom] = True
            else:
                self.revealed_symptoms[symptom] = False

            self.cumulative_cost += 0.05
            step_reward = 0.002 if symptom in self.current_case["symptoms"] else 0.001
            reward = TriageReward(total=step_reward, accuracy_score=0.005, cost_penalty=max(0.005, min(0.995, self.cumulative_cost)), done=False, message=f"Asked about {symptom}")
            return self._get_obs(), reward.total, False, {"grader_score": step_reward, "detailed_reward": reward.model_dump()}

        elif action.action_type == "order_test":
            test = action.test_name
            if test in self.current_case["vitals"]:
                self.revealed_vitals[test] = self.current_case["vitals"][test]

            self.cumulative_cost += 0.1
            step_reward = 0.003 if test in self.current_case["vitals"] else 0.001
            reward = TriageReward(total=step_reward, accuracy_score=0.005, cost_penalty=max(0.005, min(0.995, self.cumulative_cost)), done=False, message=f"Ordered test: {test}")
            return self._get_obs(), reward.total, False, {"grader_score": step_reward, "detailed_reward": reward.model_dump()}

        elif action.action_type == "triage":
            reward = compute_reward(action, self.current_case["gold"], self.cumulative_cost)
            self.is_done = True
            return self._get_obs(), reward.total, True, {"grader_score": reward.total, "detailed_reward": reward.model_dump()}

        else:
            raise ValueError(f"Unknown action type: {action.action_type}")

    def state(self) -> Dict[str, Any]:
        """Returns the full ground truth case data."""
        return self.current_case

    def _get_obs(self) -> PatientObservation:
        c = self.current_case
        total_fields = len(c["symptoms"]) + len(c["vitals"])
        revealed_fields = len(self.revealed_symptoms) + len(self.revealed_vitals)
        # Clamp away from 0.0 and 1.0 so it's always strictly in (0, 1)
        completeness = max(0.01, min(0.99, revealed_fields / total_fields)) if total_fields > 0 else 0.01
        return PatientObservation(
            patient_id=c["id"],
            age=c["age"],
            presenting_complaint=c["presenting_complaint"],
            symptoms=self.revealed_symptoms,
            vitals=self.revealed_vitals,
            history=c["history"],
            available_actions=self._get_available_actions(),
            data_completeness=completeness
        )

    def _get_available_actions(self) -> list:
        # Pull actual symptoms/vitals from the current case instead of hardcoding
        possible_symptoms = self.current_case["symptoms"]
        possible_tests = list(self.current_case["vitals"].keys())
        
        actions = [f"ask_symptom({s})" for s in possible_symptoms if s not in self.revealed_symptoms]
        actions += [f"order_test({t})" for t in possible_tests if t not in self.revealed_vitals]
        actions += ["triage"]
        return actions