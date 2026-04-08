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
from app.tasks import TASKS

client = OpenAI(
    base_url=os.getenv("API_BASE_URL"),
    api_key=os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
)

MODEL = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
BENCHMARK = "clinical-triage-env"
MAX_CASES = int(os.getenv("MAX_CASES", "5"))

env = ClinicalTriageEnv()
tasks = ["easy_triage", "medium_triage", "hard_triage"]


def extract_json(content: str):
    content = re.sub(r"```json|```", "", content).strip()
    match = re.search(r"\{.*\}", content, re.DOTALL)
    return json.loads(match.group(0)) if match else None


def get_agent_action(obs, history: List[Dict]) -> TriageAction:
    available_symptoms = [
        a.removeprefix("ask_symptom(").removesuffix(")")
        for a in obs.available_actions if a.startswith("ask_symptom(")
    ]
    available_tests = [
        a.removeprefix("order_test(").removesuffix(")")
        for a in obs.available_actions if a.startswith("order_test(")
    ]

    prompt = f"""
You are a clinical triage assistant. Triage the patient accurately with minimal steps.

Available symptoms to ask about: {available_symptoms}
Available tests to order: {available_tests}

Actions:
- {{"action_type": "ask_symptom", "symptom_name": "<name from available symptoms list>"}} (Cost: 0.05)
- {{"action_type": "order_test", "test_name": "<name from available tests list>"}} (Cost: 0.10)
- {{"action_type": "triage", "urgency_level": 1-5, "care_pathway": "ER/urgent_care/GP/self_care", "critical_flags": ["<relevant flags>"], "confidence": 0-1}}

Urgency scale: 1=Critical(life-threatening), 2=Emergency, 3=Urgent, 4=Semi-urgent, 5=Non-urgent
For critical_flags, include relevant observed symptoms/vitals (e.g. "chest_pain", "low_bp", "low_spo2", "tachycardia", "fever").

Current Patient State:
{obs.model_dump_json(indent=2)}

Step History:
{json.dumps(history, indent=2)}

Output ONLY valid JSON.
"""
    try:
        import time
        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                break
            except Exception as e:
                if "429" in str(e) and attempt < 2:
                    time.sleep(2 ** attempt)  # 1s, 2s
                    continue
                raise
        content = response.choices[0].message.content
        action_dict = extract_json(content)

        if not action_dict:
            if step_count >= 5:
                return FinalTriageAction(
                    action_type="triage",
                    urgency_level=3,
                    care_pathway="ER",
                    critical_flags=[],
                    confidence=0.3
                )
            return AskSymptomAction(symptom_name="none")

        if action_dict.get("action_type") == "triage":
            return FinalTriageAction(**action_dict)
        elif action_dict.get("action_type") == "ask_symptom":
            return AskSymptomAction(**action_dict)
        elif action_dict.get("action_type") == "order_test":
            return OrderTestAction(**action_dict)

        return AskSymptomAction(symptom_name="none")
    except Exception as e:
        print(f"[WARN] get_agent_action error: {type(e).__name__}: {e}", file=sys.stderr)
        return AskSymptomAction(symptom_name="none")


# --- Run tasks ---
cases_run = 0
for task_id in tasks:
    for case_id in TASKS[task_id]:
        if cases_run >= MAX_CASES:
            break
        step_count = 0
        history = []
        reward = None
        last_error = None
        step_rewards = []
        success = False

        try:
            obs = env.reset(task_id, case_id=case_id)
            done = False

            print(f"[START] task={task_id} env={BENCHMARK} model={MODEL}")

            while not done and step_count < 10:
                action = get_agent_action(obs, history)
                action_str = json.dumps(action.model_dump(), separators=(',', ':'))

                try:
                    obs, reward, done, info = env.step(action)
                    last_error = info.get("error", None) if info else None
                    # User-provided clamping and metadata logic
                    r = info.get("grader_score", 0.01) or 0.01
                    r = max(0.001, min(0.999, r))
                except Exception as exc:
                    print(f"[DEBUG] Task {task_id} error: {exc}", flush=True)
                    r = 0.001  # never exactly 0
                    done = True

                step_count += 1
                step_rewards.append(r)
                error_str = last_error if last_error else "null"
                done_str = "true" if done else "false"

                print(f"[STEP] step={step_count} action={action_str} reward={r:.4f} done={done_str} error={error_str}")

                history.append({"step": step_count, "action": action.model_dump(), "reward": r})

            success = done and (reward.total > 0 if reward else False)

        except Exception as e:
            last_error = str(e)
            print(f"[ERROR] task={task_id} case={case_id}: {e}", file=sys.stderr)

        finally:
            if hasattr(env, 'close'):
                env.close()
            rewards_str = ",".join(f"{r:.4f}" for r in step_rewards)
            success_str = "true" if success else "false"
            print(f"[END] success={success_str} steps={step_count} rewards={rewards_str}")
            cases_run += 1
    if cases_run >= MAX_CASES:
        break