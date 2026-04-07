from dotenv import load_dotenv
load_dotenv()

import os
import json
import re
import sys
from openai import OpenAI
from typing import List, Dict

from app.env import ClinicalTriageEnv
from app.models import TriageAction, FinalTriageAction, AskSymptomAction, OrderTestAction

client = OpenAI(
    base_url=os.getenv("API_BASE_URL"),
    api_key=os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
)

MODEL = os.getenv("MODEL_NAME", "gpt-4o")
BENCHMARK = "clinical-triage-env"

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

Decide your next action. Output ONLY valid JSON.
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
            return AskSymptomAction(symptom_name="none")

        if action_dict.get("action_type") == "triage":
            return FinalTriageAction(**action_dict)
        elif action_dict.get("action_type") == "ask_symptom":
            return AskSymptomAction(**action_dict)
        elif action_dict.get("action_type") == "order_test":
            return OrderTestAction(**action_dict)

        return AskSymptomAction(symptom_name="none")
    except Exception:
        return AskSymptomAction(symptom_name="none")


# --- Run tasks ---
for task_id in tasks:
    step_count = 0
    history = []
    reward = None
    last_error = None
    step_rewards = []
    success = False

    try:
        obs = env.reset(task_id)
        done = False

        print(f"[START] task={task_id} env={BENCHMARK} model={MODEL}")

        while not done and step_count < 10:
            action = get_agent_action(obs, history)
            action_str = json.dumps(action.model_dump(), separators=(',', ':'))

            try:
                obs, reward, done, info = env.step(action)
                last_error = info.get("error", None) if info else None
                r = reward.total
            except Exception as e:
                last_error = str(e)
                r = 0.0
                done = True

            step_count += 1
            step_rewards.append(r)
            error_str = last_error if last_error else "null"
            done_str = "true" if done else "false"

            print(f"[STEP] step={step_count} action={action_str} reward={r:.2f} done={done_str} error={error_str}")

            history.append({"step": step_count, "action": action.model_dump(), "reward": r})

        success = done and (reward.total > 0 if reward else False)

    except Exception as e:
        last_error = str(e)
        print(f"[START] task={task_id} env={BENCHMARK} model={MODEL}", file=sys.stderr)

    finally:
        rewards_str = ",".join(f"{r:.2f}" for r in step_rewards)
        success_str = "true" if success else "false"
        print(f"[END] success={success_str} steps={step_count} rewards={rewards_str}")
        env.close() if hasattr(env, 'close') else None