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

Intermediate steps give small positive reward for revealing relevant information, penalized by action cost. The final triage action yields a score in [0, 1] based on:

- **Urgency accuracy** (40%) — how close to gold urgency level
- **Care pathway** (35%) — exact match = 1.0, adjacent ER/urgent_care = 0.7
- **Critical flags** (25%) — F1 score of predicted vs gold flags
- **Cost penalty** — cumulative action costs subtracted from final score

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
cp .env.example .env   # fill in your API credentials
python inference.py

# Docker
docker build -t clinical-triage-env .
docker run --rm --env-file .env clinical-triage-env
```

## Environment Variables

| Variable | Description |
|---|---|
| `HF_TOKEN` | API key (Groq, HuggingFace, or OpenAI) |
| `API_BASE_URL` | Base URL for OpenAI-compatible API |
| `MODEL_NAME` | Model identifier |

## OpenEnv Interface

```python
from app.env import ClinicalTriageEnv

env = ClinicalTriageEnv()
obs = env.reset("easy_triage")       # PatientObservation
obs, reward, done, info = env.step(action)  # TriageReward
state = env.state()                  # full ground truth
```
