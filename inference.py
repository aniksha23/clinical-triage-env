from dotenv import load_dotenv
load_dotenv()

import os
import json
import re
from openai import OpenAI
from typing import List, Dict, Any

from app.env import ClinicalTriageEnv
from app.models import TriageAction, FinalTriageAction, AskSymptomAction, OrderTestAction

# --- Setup client ---
client = OpenAI(
    base_url=os.getenv("API_BASE_URL"),
    api_key=os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
)

MODEL = os.getenv("MODEL_NAME", "gpt-4o")

env = ClinicalTriageEnv()
tasks = ["easy_triage", "medium_triage", "hard_triage"]


def extract_json(content: str):
    content = re.sub(r"```json|```", "", content).strip()
    match = re.search(r"\{.*\}", content, re.DOTALL)
    return json.loads(match.group(0)) if match else None


def get_agent_action(obs, history: List[Dict]) -> TriageAction:
    prompt = f"""
You are a clinical triage assistant. Your goal is to accurately triage the patient while minimizing unnecessary steps.

Available Actions:
- {{"action_type": "ask_symptom", "symptom_name": "symptom_id"}} (Cost: 0.05)
- {{"action_type": "order_test", "test_name": "test_id"}} (Cost: 0.10)
- {{"action_type": "triage", "urgency_level": 1-5, "care_pathway": "ER/urgent_care/GP/self_care", "critical_flags": [], "confidence": 0-1}} (Ends episode)

Patient Observation:
{obs.model_dump_json(indent=2)}

Step History:
{json.dumps(history, indent=2)}

Decide your next action. Output ONLY valid JSON of the action you wish to take.
"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        content = response.choices[0].message.content
        action_dict = extract_json(content)
        
        if not action_dict:
            return AskSymptomAction(symptom_name="none") # Fallback

        # Basic normalization
        if action_dict.get("action_type") == "triage":
            return FinalTriageAction(**action_dict)
        elif action_dict.get("action_type") == "ask_symptom":
            return AskSymptomAction(**action_dict)
        elif action_dict.get("action_type") == "order_test":
            return OrderTestAction(**action_dict)
        
        return AskSymptomAction(symptom_name="none")
    except Exception as e:
        print(f"Error getting action: {e}")
        return AskSymptomAction(symptom_name="none")


# --- Run tasks ---
results = []

for task_id in tasks:
    obs = env.reset(task_id)
    done = False
    step_count = 0
    history = []
    
    print(f"\n>>> Starting Task: {task_id}")
    
    while not done and step_count < 10:
        action = get_agent_action(obs, history)
        obs, reward, done, _ = env.step(action)
        
        step_info = {
            "step": step_count,
            "action": action.model_dump(),
            "reward": reward.total,
            "message": reward.message
        }
        history.append(step_info)
        
        print(json.dumps(step_info))
        step_count += 1

    print(f"--- Task Ended: {task_id} | Final Reward: {reward.total:.2f} | Steps: {step_count}")
    results.append({
        "task_id": task_id,
        "total_reward": reward.total,
        "accuracy": reward.accuracy_score,
        "cost": reward.cost_penalty,
        "steps": step_count
    })

print("\n\n" + "="*30)
print("FINAL EVALUATION RESULTS")
print("="*30)
for res in results:
    print(f"{res['task_id']}: Reward={res['total_reward']:.2f} (Acc={res['accuracy']:.2f}, Cost={res['cost']:.2f})")