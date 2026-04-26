import os
import json
import time
from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.queue_env import ClinicalQueueEnv
from app.models import TriageAction, TriageQueueAction, AskSymptomAction, OrderTestAction
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
MODEL = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")

def get_hallway_action(obs, notepad_str, step_count) -> TriageAction:
    active_pid = obs.active_patient.patient_id if obs.active_patient else "None"
    
    prompt = f"""
    ER HALLWAY STATUS:
    {notepad_str}
    
    ACTIVE PATIENT: {active_pid}
    STEP: {step_count}/15
    
    MISSION: 
    1. Assess both patients quickly.
    2. Once you have a primary clue for each, SUBMIT the sorted queue.
    3. DO NOT get stuck on one patient. If you have some info for P1, switch to P2.
    
    AVAILABLE ACTIONS:
    - {{"action_type": "ask_symptom", "patient_id": "P1/P2", "symptom_name": "<symptom>"}}
    - {{"action_type": "order_test", "patient_id": "P1/P2", "test_name": "BP/HR/ECG/WBC/Temp"}}
    - {{"action_type": "submit_triage_queue", "queue": [{{"patient_id": "P1", "assigned_urgency": 1-5, "reasoning": "..."}}, ...]}}
    
    Output ONLY JSON.
    """
    
    system = "You are a senior triage nurse. Efficiency is life. Triage critical patients (Level 1) immediately."
    
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                temperature=0,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            atype = data.get("action_type")
            if atype == "ask_symptom": return AskSymptomAction(**data)
            if atype == "order_test": return OrderTestAction(**data)
            if atype == "submit_triage_queue": return TriageQueueAction(**data)
        except Exception:
            time.sleep(1)
    return AskSymptomAction(patient_id="P1", symptom_name="chest_pain")

# --- EXECUTION ---
env = ClinicalQueueEnv(num_patients=2)
obs = env.reset()
done = False
step = 0
global_findings = {}

print(f"[START] Hallway Triage Simulation | 2 Patients | Goal: Sorted Queue")

while not done and step < 15:
    step += 1
    if obs.active_patient:
        pid = obs.active_patient.patient_id
        if pid not in global_findings: global_findings[pid] = {"symptoms": {}, "vitals": {}}
        global_findings[pid]["symptoms"].update(obs.active_patient.symptoms)
        global_findings[pid]["vitals"].update(obs.active_patient.vitals)

    notepad_str = ""
    for p in obs.waiting_room:
        pid = p.patient_id
        f = global_findings.get(pid, {"symptoms": {}, "vitals": {}})
        notepad_str += f"- {pid}: {p.presenting_complaint}\n  Known Findings: {f['symptoms']} {f['vitals']}\n"

    action = get_hallway_action(obs, notepad_str, step)
    obs, reward, done, info = env.step(action)
    
    # IMPROVED LOGGING: Show exactly what the agent is asking
    detail = ""
    if action.action_type == "ask_symptom": detail = f"({action.symptom_name})"
    elif action.action_type == "order_test": detail = f"({action.test_name})"
    
    print(f"[STEP {step}] Action: {action.action_type}{detail} Target: {getattr(action,'patient_id','N/A')} Reward: {reward:.4f}")
    if done: print(f"[RESULT] {info.get('msg')}")
    time.sleep(8) 

print(f"[END] Hallway Finished. Final Score: {reward:.4f}")
