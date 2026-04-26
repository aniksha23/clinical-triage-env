---
title: Clinical Triage Env v2
emoji: 🏥
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# 🏥 Clinical Triage Agent: RL-Optimized Patient Prioritization
**Built for the Meta PyTorch OpenEnv Hackathon x SST**

[![Demo Video](https://img.shields.io/badge/📺%20Watch-2%20Min%20Demo-red)](https://youtube.com/your-link-here)
[![Model on HF](https://img.shields.io/badge/🤗%20Hugging%20Face-Model-blue)](https://huggingface.co/sreeya14/clinical-v2-final)
[![Space on HF](https://img.shields.io/badge/🤗%20Hugging%20Face-Live%20Env-green)](https://huggingface.co/spaces/sreeya14/clinical-v2)

## ⚡ TL;DR
An OpenEnv-compatible Reinforcement Learning environment that teaches LLM agents clinical triage as an information-gathering problem with multi-patient queue orchestration. Agents must actively probe patients to surface hidden risks—including suicidal ideation—and rank them under time pressure. Reviewed by a psychiatry professor at NIMHANS.

## 📊 End-to-End RL Training Results
![End-to-End RL Training](hackathon_final_plots.png) 
> *Left: Our GRPO-trained agent escaping the penalty baseline to reach clinical stability. Right: The behavioral shift proving the agent stopped spamming irrelevant tests (wasted time) and learned to execute targeted 'Golden Probes'.*

---

## 🧠 Why This Matters: The Credit Assignment Problem
Most clinical AI projects treat triage as a simple open-loop text classification problem. But in the real world, patients minimize, deflect, or hide their true symptoms. Standard zero-shot LLMs collapse under this state uncertainty.

We engineered an environment so complex that it explicitly exposes the **Credit Assignment Problem** in LLM reasoning. By structuring the ER queue as a strict **Partially Observable Markov Decision Process (POMDP)**, we demonstrate that an agent must learn an *Active Exploration Policy* rather than just guessing. Our environment provides a built-in Dense Information Gain (IG) reward matrix, making it a turnkey testbed for researchers evaluating RL algorithms (like GRPO) on long-horizon reasoning.

### Hackathon Theme Fit
* **Primary:** Theme #3.1 — Professional Tasks (World modeling under partial observability, resisting shortcuts).
* **Secondary:** Theme #2 — Long-Horizon Planning (Multi-step probing → individual triage → holistic queue ranking).

---

## ⚙️ Core RL Design Mechanisms
To max out the learning signal for our GRPO training, we engineered three specific mechanisms into the environment:

1. **State-Space Discovery (The POMDP Feature):** Symptoms and critical risks are explicitly hidden (`hidden_facts` in `data.py`). The agent cannot shortcut to a diagnosis; it is forced to learn an *Active Exploration Policy* to uncover the truth.
2. **Intrinsic Information Gain (IG) Rewards:** We built a `discovery_values` dictionary into the reward function. The environment dynamically rewards the model for asking the *right* questions (e.g., yielding a massive `+0.30` reward for successfully uncovering hidden suicidal ideation).
3. **Safety-Constrained Ranking (Asymmetric Penalties):** To enforce real-world safety alignment, we implemented asymmetric penalty multipliers (`order_score *= 0.2`). Failing to place a Level-1 critical patient in the top 2 queue slots geometrically destroys the agent's episode score, forcing the model to prioritize systemic safety over individual patient completion.

### Reward Structure
| Component | Value | Rationale |
|---|---|---|
| Per-step time penalty | `-0.01` | Simulates clinical time pressure. |
| Probe (relevant category) | `+0.05` to `+0.30` | Discovery-weighted by clinical utility. |
| Probe (irrelevant) | `0.00` | No value, incurs the step time penalty. |
| Per-patient triage (correct level) | `+0.50` | Rewards accuracy. |
| Per-patient triage (off by 1) | `+0.20` | Partial credit for close calls. |
| Per-patient triage (off by 2+) | `-0.50` | Asymmetric penalty—under-triage hurts. |
| Auto-submit queue ranking | Up to `+1.00` | Rewards correct systemic prioritization. |
| Junk action (empty/invalid) | `-0.10` | Burns out gaming attempts and hallucinations. |

---

## 📋 Clinical Scenarios
Scenarios were reviewed and refined with input from a psychiatry professor at NIMHANS (National Institute of Mental Health and Neurosciences).

| ID | Case | Hidden Risk | Gold ESI | Probe Required |
|---|---|---|---|---|
| `case_cardiac_001` | 58M, "chest heaviness" | Anterior MI (ST elevation) | 1 | `pain_characterization` → `ECG` |
| `case_mental_001` | 24F, "feeling down" | **Active suicidal ideation** | 1 | `mental_status` → `suicide_screening` |
| `case_abdominal_001` | 35M, "stomach hurts" | Appendicitis | 2 | `pain_characterization` → `physical_exam` |
| `case_stroke_001` | 68F, "feels weird" | Stroke (FAST positive) | 1 | `neuro_exam` |
| `case_low_acuity_001` | 25M, ankle sprain | None | 4-5 | minimal probing |
| `case_sepsis_001` | 70F, confusion | Sepsis | 1-2 | `vitals` + `WBC` |

---

## 🔍 Behavior Comparison (The Suicidal Ideation Case)
This trajectory demonstrates how training fundamentally shifts the model from surface-level guessing to active clinical investigation.

```text
PATIENT P2: 24F, "feeling really down lately"
HIDDEN: Active suicidal ideation, plan with means

UNTRAINED AGENT                          │    TRAINED / HEURISTIC AGENT
─────────────────────────────────────────┼──────────────────────────────────────────────
1. ask_symptom(headache)                 │    1. ask_symptom(mental_status_screening)
   → "I'm not sure"                      │       → "Flat affect, hopelessness"
   reward: -0.01                         │       reward: +0.15
                                         │
2. ask_symptom(fever)                    │    2. ask_symptom(suicidal_ideation_screening)
   → "I'm not sure"                      │       → "Thinking about pills tonight"
   reward: -0.01                         │       reward: +0.30
                                         │
3. triage(level=4, GP)                   │    3. triage(level=1, ER, [suicide_risk])
   ❌ MISSED RISK                        │       ✓ RISK CAUGHT
   episode reward: -0.50                 │       episode reward: +1.50