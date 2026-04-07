from dotenv import load_dotenv
load_dotenv()

import os
import json
import re
from openai import OpenAI

from app.env import ClinicalTriageEnv
from app.models import TriageAction

# --- Setup client ---
client = OpenAI(
    base_url=os.getenv("API_BASE_URL"),
    api_key=os.getenv("HF_TOKEN")
)

MODEL = os.getenv("MODEL_NAME")

env = ClinicalTriageEnv()

tasks = ["easy_triage", "medium_triage", "hard_triage"]


# --- Robust JSON extractor ---
def extract_json(content: str):
    # Remove markdown formatting
    content = re.sub(r"```json|```", "", content).strip()

    # Extract JSON object
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if not match:
        return None

    json_str = match.group(0)

    try:
        return json.loads(json_str)
    except:
        return None


# --- Fallback action (never crash) ---
def fallback_action():
    return {
        "urgency_level": 3,
        "care_pathway": "GP",
        "critical_flags": [],
        "confidence": 0.5
    }


# --- Run tasks ---
for task_id in tasks:
    obs = env.reset(task_id)

    print(json.dumps({
        "event": "START",
        "task_id": task_id,
        "model": MODEL
    }))

    prompt = f"""
You are a clinical triage assistant.

STRICT RULES:
- Output ONLY valid JSON
- No explanation
- No markdown
- No text outside JSON

FORMAT:
{{
  "urgency_level": 1,
  "care_pathway": "ER",
  "critical_flags": ["example"],
  "confidence": 0.5
}}

Patient:
{obs.model_dump_json()}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.choices[0].message.content

        # Debug (optional, can remove later)
        print("RAW OUTPUT:", content)

        action_dict = extract_json(content)

        if action_dict is None:
            print("⚠️ JSON parse failed → fallback")
            action_dict = fallback_action()

    except Exception as e:
        print("⚠️ API error → fallback:", str(e))
        action_dict = fallback_action()

    # Ensure valid schema
    try:
        action = TriageAction(**action_dict)
    except:
        print("⚠️ Invalid schema → fallback")
        action = TriageAction(**fallback_action())

    obs, reward, done, _ = env.step(action)

    print(json.dumps({
        "event": "STEP",
        "step": 0,
        "action": action.model_dump(),
        "reward": reward.total,
        "done": done
    }))

    print(json.dumps({
        "event": "END",
        "task_id": task_id,
        "total_reward": reward.total,
        "scores": {
            "urgency": reward.urgency_score,
            "pathway": reward.pathway_score,
            "flags": reward.flags_score
        }
    }))