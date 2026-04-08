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
    base_url=os.environ.get("API_BASE_URL"),
    api_key=os.environ.get("API_KEY")
)

MODEL = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
BENCHMARK = "clinical-triage-env"
MAX_CASES_PER_TASK = int(os.getenv("MAX_CASES", "2"))  # per task, not global

env = ClinicalTriageEnv()
tasks = ["easy_triage", "medium_triage", "hard_triage"]


def extract_json(content: str):
    content = re.sub(r"```json|```", "", content).strip()
    match = re.search(r"\{.*\}", content, re.DOTALL)
    return json.loads(match.group(0)) if match else None


def get_agent_action(obs, history: List[Dict], step_count: int) -> TriageAction:
    unrevealed_tests = [
        a.removeprefix("order_test(").removesuffix(")")
        for a in obs.available_actions if a.startswith("order_test(")
    ]

    prompt = f"""
You are a clinical triage assistant. Triage the patient accurately with minimal steps.

Current Patient State:
{obs.model_dump_json(indent=2)}

Step History:
{json.dumps(history, indent=2)}

Available Actions (choose exactly one):
- {{"action_type": "ask_symptom", "symptom_name": "<any clinically relevant symptom you want to probe>"}} (Cost: 0.05)
- {{"action_type": "order_test", "test_name": "<one of: {unrevealed_tests}>"}} (Cost: 0.10)
- {{"action_type": "triage", "urgency_level": 1-5, "care_pathway": "ER/urgent_care/GP/self_care", "critical_flags": ["<flags>"], "confidence": 0.0-1.0}}

Rules:
- For ask_symptom: choose symptoms based on clinical reasoning — you are NOT given a list, use your medical knowledge
- For order_test: you MUST use one of the exact test names listed above
- Urgency: 1=Critical, 2=Emergency, 3=Urgent, 4=Semi-urgent, 5=Non-urgent
- critical_flags examples: "chest_pain", "low_bp", "low_spo2", "tachycardia", "fever", "confusion"
- Stop gathering info and triage once you have enough to decide confidently

Output ONLY valid JSON, nothing else.
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


# --- Run tasks --- (MAX_CASES_PER_TASK cases per task, so all 3 tasks always get output)
for task_id in tasks:
    cases_in_task = 0
    for case_id in TASKS[task_id]:
        if cases_in_task >= MAX_CASES_PER_TASK:
            break
        step_count = 0
        history = []
        reward = None
        last_error = None
        step_rewards = []
        final_score = 0.005  # floor — never exactly 0

        try:
            obs = env.reset(task_id, case_id=case_id)
            done = False

            print(f"[START] task={task_id} env={BENCHMARK} model={MODEL}", flush=True)

            while not done and step_count < 10:
                action = get_agent_action(obs, history, step_count)
                action_str = json.dumps(action.model_dump(), separators=(',', ':'))

                try:
                    obs, reward, done, info = env.step(action)
                    last_error = info.get("error", None) if info else None
                    r = max(0.005, min(0.995, reward))
                    if done:
                        final_score = r
                except Exception as e:
                    last_error = str(e)
                    r = 0.005  # never exactly 0
                    done = True

                step_count += 1
                step_rewards.append(r)
                error_str = last_error if last_error else "null"
                done_str = "true" if done else "false"

                print(f"[STEP] step={step_count} action={action_str} reward={r:.3f} done={done_str} error={error_str}", flush=True)

                history.append({"step": step_count, "action": action.model_dump(), "reward": r})

        except Exception as e:
            last_error = str(e)
            final_score = 0.005  # floor so crashed task never emits score=0.000
            print(f"[DEBUG] Task {task_id} error: {e}", file=sys.stderr, flush=True)

        finally:
            if hasattr(env, 'close'):
                env.close()
            rewards_str = ",".join(f"{r:.3f}" for r in step_rewards)
            success_val = 0.995 if (reward is not None and reward > 0 and done) else 0.005
            print(f"[END] task={task_id} success={success_val:.3f} steps={step_count} score={final_score:.3f} rewards={rewards_str}", flush=True)
            cases_in_task += 1
