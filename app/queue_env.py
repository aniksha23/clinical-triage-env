# app/queue_env.py
import random
from typing import List, Dict, Any, Tuple, Optional

from app.data import SCENARIOS
from app.models import (
    PatientObservation, QueueObservation, PatientSummary, 
    TriageAction, TriageReward, TriageQueueAction
)
from app.patient_simulator import PatientScenario, PatientSimulator
from app.queue_grader import compute_queue_reward

class ClinicalQueueEnv:
    def __init__(self, num_patients: int = 4):
        self.num_patients = num_patients
        self.patients: Dict[str, PatientSimulator] = {}
        self.patient_scenarios: Dict[str, Dict] = {}
        self.active_patient_id: Optional[str] = None
        self.global_step_id = 0
        self.patient_states: Dict[str, Dict[str, Any]] = {}
        self.is_done = False

    def reset(self) -> QueueObservation:
        self.global_step_id = 0
        self.is_done = False
        self.patients = {}
        self.patient_scenarios = {}
        self.patient_states = {}
        
        selected_scenarios = random.sample(SCENARIOS, min(self.num_patients, len(SCENARIOS)))
        for i, data in enumerate(selected_scenarios):
            p_id = f"P{i+1}"
            scenario = PatientScenario(
                case_id=p_id,
                chief_complaint=data["presenting_complaint"],
                demographics=data["demographics"],
                hidden_facts=data["hidden_facts"],
                reveal_map=data["reveal_map"],
                test_results=data["test_results"],
                discovery_values=data.get("discovery_values", {})
            )
            self.patients[p_id] = PatientSimulator(scenario)
            self.patient_scenarios[p_id] = data
            self.patient_states[p_id] = {
                "revealed_symptoms": {},
                "revealed_vitals": {},
                "cumulative_cost": 0.0
            }
        self.active_patient_id = None
        return self._get_obs()

    def step(self, action: TriageAction) -> Tuple[QueueObservation, float, bool, Dict[str, Any]]:
        self.global_step_id += 1
        info = {"msg": ""}
        
        # --- GLOBAL PRESSURE: -0.01 per hallway step ---
        reward = -0.01

        # 1. AUTO-SWITCH FOCUS
        if hasattr(action, 'patient_id') and action.patient_id in self.patients:
            self.active_patient_id = action.patient_id

        # 2. SUBMIT QUEUE (Final Action)
        if action.action_type == "submit_triage_queue":
            reward = compute_queue_reward(action, self.patient_scenarios)
            self.is_done = True
            info["msg"] = f"Queue Submitted. Accuracy: {reward:.4f}"
            return self._get_obs(), reward, True, info

        # 3. INTERVIEW ACTIVE PATIENT
        elif self.active_patient_id:
            p_id = self.active_patient_id
            sim = self.patients[p_id]
            state = self.patient_states[p_id]
            
            # Burn the 'none' path
            if action.action_type == "ask_symptom" and (not action.symptom_name or action.symptom_name == "none"):
                return self._get_obs(), -0.10, False, {"msg": "FAILURE: Asked 'none'"}

            if action.action_type == "ask_symptom":
                res = sim.handle_question(action.symptom_name)
                state["revealed_symptoms"][action.symptom_name] = res
                reward += sim.last_step_ig
            
            elif action.action_type == "order_test":
                res = sim.handle_test(action.test_name)
                state["revealed_vitals"][action.test_name] = res
                reward += sim.last_step_ig

        return self._get_obs(), reward, False, info

    def _get_obs(self) -> QueueObservation:
        waiting_room = []
        for p_id, sim in self.patients.items():
            waiting_room.append(PatientSummary(
                patient_id=p_id,
                age=sim.scenario.demographics.get("age", 0),
                presenting_complaint=sim.scenario.chief_complaint,
                urgency_hint="Needs assessment"
            ))
        active_obs = None
        if self.active_patient_id:
            p_id = self.active_patient_id
            sim = self.patients[p_id]
            state = self.patient_states[p_id]
            active_obs = PatientObservation(
                patient_id=p_id,
                age=sim.scenario.demographics.get("age", 0),
                presenting_complaint=sim.scenario.chief_complaint,
                symptoms=state["revealed_symptoms"],
                vitals=state["revealed_vitals"],
                observations=sim.get_current_observations(),
                history=[],
                available_actions=["ask_symptom", "order_test", "submit_triage_queue"],
                data_completeness=0.5
            )
        return QueueObservation(waiting_room=waiting_room, active_patient=active_obs, current_time_step=self.global_step_id)
