# app/env.py
import random
from typing import Tuple, Dict, Any

from app.data import SCENARIOS
from app.tasks import TASKS
from app.models import PatientObservation, TriageAction, TriageReward, FinalTriageAction
from app.grader import compute_reward
from app.patient_simulator import PatientScenario, PatientSimulator

class ClinicalTriageEnv:
    def __init__(self):
        self.simulator = None
        self.current_case_data = None
        self.cumulative_cost = 0.0
        self.is_done = False
        self.step_id = 0
        self.revealed_symptoms = {} 
        self.revealed_vitals = {}   
        self.last_error = None

    def reset(self, task_id: str, case_id: str = None) -> PatientObservation:
        case_ids = TASKS.get(task_id, [])
        if not case_ids:
            case_ids = [s["id"] for s in SCENARIOS]

        if case_id:
            case_data = next((c for c in SCENARIOS if c["id"] == case_id), None)
        else:
            valid_scenarios = [s for s in SCENARIOS if s["id"] in case_ids]
            case_data = random.choice(valid_scenarios) if valid_scenarios else random.choice(SCENARIOS)
        
        self.current_case_data = case_data
        
        scenario = PatientScenario(
            case_id=case_data["id"],
            chief_complaint=case_data["presenting_complaint"],
            demographics=case_data["demographics"],
            hidden_facts=case_data["hidden_facts"],
            reveal_map=case_data["reveal_map"],
            test_results=case_data["test_results"],
            generic_responses=case_data.get("generic_responses", {}),
            discovery_values=case_data.get("discovery_values", {})
        )
        self.simulator = PatientSimulator(scenario)
        
        self.revealed_symptoms = {}
        self.revealed_vitals = {}
        self.cumulative_cost = 0.0
        self.is_done = False
        self.step_id = 0
        self.last_error = None
        
        return self._get_obs()

    def step(self, action: TriageAction) -> Tuple[PatientObservation, float, bool, Dict[str, Any]]:
        if self.is_done:
            raise RuntimeError("Episode is already done. Call reset().")
        
        self.step_id += 1
        info = {"msg": ""}
        
        # --- THE PRESSURE GRADIENT: -0.01 per step (The clock is ticking) ---
        base_step_penalty = -0.01 
        reward = base_step_penalty

        # 1. HANDLE JUNK ACTIONS (Hard Penalty)
        if action.action_type == "ask_symptom" and (not action.symptom_name or action.symptom_name == "none"):
            reward = -0.10 # Burn the 'none' path
            return self._get_obs(), reward, False, {"message": "CRITICAL FAILURE: Invalid/Empty question"}

        # 2. INTERVIEW LOGIC
        if action.action_type == "ask_symptom":
            symptom = action.symptom_name
            response = self.simulator.handle_question(symptom)
            self.revealed_symptoms[symptom] = response
            
            # Repetition check (The Simulator already flags 'already told you')
            if "already told you" in response or "annoyed" in response:
                reward = -0.05 # Redundancy penalty
            else:
                # Add Information Gain Spike
                reward += self.simulator.last_step_ig
            
            info["message"] = f"Asked: {symptom}"

        elif action.action_type == "order_test":
            test = action.test_name
            response = self.simulator.handle_test(test)
            self.revealed_vitals[test] = str(response)
            
            # Add Information Gain Spike (Useful tests spike, useless ones stay near-zero)
            reward += self.simulator.last_step_ig
            info["message"] = f"Ordered: {test}"

        elif action.action_type == "triage":
            # The Final Reward (compute_reward already handles decay and cost)
            final_reward_obj = compute_reward(
                action, 
                self.current_case_data["gold"], 
                self.cumulative_cost, 
                self.step_id
            )
            self.is_done = True
            return self._get_obs(), final_reward_obj.total, True, {"detailed_reward": final_reward_obj.model_dump()}

        # 3. Cumulative Cost Tracking (External to immediate reward)
        self.cumulative_cost += (0.05 if action.action_type == "ask_symptom" else 0.10)

        # Ensure reward isn't exactly zero for LLM visibility
        step_reward = max(-0.5, min(0.99, reward))
        return self._get_obs(), step_reward, False, info

    def _get_obs(self) -> PatientObservation:
        c = self.current_case_data
        total_facts = len(c["hidden_facts"])
        revealed_count = len(self.simulator.revealed_facts)
        completeness = max(0.005, min(0.995, revealed_count / total_facts)) if total_facts > 0 else 0.005
        
        return PatientObservation(
            patient_id=c["id"],
            age=c["age"],
            presenting_complaint=c["presenting_complaint"],
            symptoms=self.revealed_symptoms,
            vitals=self.revealed_vitals,
            observations=self.simulator.get_current_observations(),
            history=c.get("history", []),
            available_actions=self._get_available_actions(),
            data_completeness=completeness
        )

    def _get_available_actions(self) -> list:
        all_tests = list(self.current_case_data["test_results"].keys())
        unrevealed_tests = [t for t in all_tests if t not in self.revealed_vitals]
        actions = ["ask_symptom(<symptom_name>)", "triage"]
        actions += [f"order_test({t})" for t in unrevealed_tests]
        return actions