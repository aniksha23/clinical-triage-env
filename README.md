---
title: Clinical Triage Env
emoji: 🏥
colorFrom: red
colorTo: blue
sdk: docker
tags:
  - openenv
  - reinforcement-learning
  - clinical
  - triage
pinned: false
---

# Clinical Triage Environment

An AI agent environment simulating emergency department triage. The agent must gather patient information and assign the correct urgency level and care pathway — mimicking decisions made by real triage nurses.

## Observation Space

| Field | Type | Description |
|---|---|---|
| `patient_id` | str | Case identifier |
| `age` | int | Patient age |
| `presenting_complaint` | str | Chief complaint |
| `symptoms` | Dict[str, bool] | Revealed symptoms |
| `vitals` | Dict[str, float\|str] | Revealed vital signs |
| `history` | List[str] | Medical history |
| `available_actions` | List[str] | Actions available this step |
| `data_completeness` | float | Fraction of data revealed (0–1) |

## Action Space

| Action | Fields | Cost |
|---|---|---|
| `ask_symptom` | `symptom_name: str` | −0.05 |
| `order_test` | `test_name: str` | −0.10 |
| `triage` | `urgency_level: 1–5`, `care_pathway: ER/urgent_care/GP/self_care`, `critical_flags: List[str]`, `confidence: float` | final step |

## Reward

All scores are strictly in **(0, 1)** — never exactly 0 or 1.

**Intermediate steps:**

| Action | Reward |
|---|---|
| Ask about a relevant symptom | +0.10 |
| Ask about an irrelevant symptom | +0.02 |
| Order a test present in vitals | +0.15 |
| Order an unknown test | +0.02 |

**Final triage score** = `accuracy_score − cost_penalty`, clamped to (0.01, 0.99):

- **Urgency accuracy** (40%) — `1.0 − 0.4 × |predicted − gold|`
- **Care pathway** (35%) — exact match = 1.0; ER ↔ urgent_care = 0.7; otherwise 0.0
- **Critical flags** (25%) — mean of precision and recall vs gold flags
- **Cost penalty** — cumulative action costs (0.05 per symptom ask, 0.10 per test)

## Tasks

| Task | Cases | Difficulty | Description |
|---|---|---|---|
| `easy_triage` | 3 | Easy | Clear-cut presentations, complete data |
| `medium_triage` | 3 | Medium | Partial data, requires 1–2 information steps |
| `hard_triage` | 9 | Hard | Incomplete data, ambiguous presentations |

## Baseline Performance

| Task | Avg Reward | Avg Steps | Model |
|---|---|---|---|
| easy_triage | ~0.85 | 1–2 | llama-3.1-8b-instant |
| medium_triage | ~0.70 | 2–3 | llama-3.1-8b-instant |
| hard_triage | ~0.65 | 2–3 | llama-3.1-8b-instant |

## Setup

```bash
# Local
pip install -r requirements.txt
cp .env.example .env   # set API_KEY, API_BASE_URL, MODEL_NAME
python inference.py

# Docker
docker build -t clinical-triage-env .
docker run --rm -e API_KEY=... -e API_BASE_URL=... -e MODEL_NAME=... clinical-triage-env
```

The Docker image runs a FastAPI server on port 7860 (`/reset`, `/step`, `/state`, `/health`) using only the slim deps in `requirements-inference.txt`.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `API_KEY` | Yes | API key for the LLM provider (e.g. Groq) |
| `API_BASE_URL` | Yes | OpenAI-compatible base URL (e.g. `https://api.groq.com/openai/v1`) |
| `MODEL_NAME` | No | Model identifier (default: `llama-3.1-8b-instant`) |
| `MAX_CASES` | No | Max cases to run per `inference.py` invocation (default: 5) |

## OpenEnv Interface

```python
from app.env import ClinicalTriageEnv

env = ClinicalTriageEnv()
obs = env.reset("easy_triage")              # PatientObservation
obs = env.reset("easy_triage", case_id="e1")  # pin to specific case
obs, reward, done, info = env.step(action)  # TriageReward
state = env.state()                         # full ground truth (gold labels)
```

## Output Format

`inference.py` emits structured log lines consumed by the OpenEnv validator:

```
[START] task=easy_triage env=clinical-triage-env model=llama-3.1-8b-instant
[STEP]  step=1 action={...} reward=0.100 done=false error=null
[STEP]  step=2 action={...} reward=0.650 done=true  error=null
[END]   task=easy_triage success=true steps=2 score=0.650 rewards=0.100,0.650
```
