---
title: Clinical Triage Agent v2
emoji: 🏥
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# 🏥 Clinical Triage Agent: The Strategic POMDP Reasoner
**Built for the Meta PyTorch OpenEnv Hackathon x India 2026**

### ⚡ Quick Links
*   **[🤗 Live Hugging Face Space](https://huggingface.co/spaces/sreeya14/clinical-v2)** (Try the Live Env)
*   **[🤗 Model Weights (GRPO-Trained)](https://huggingface.co/sreeya14/clinical-v2-final)**
*   **[📺 Pitch Demo](https://youtube.com/your-demo-link)**


---

## 1. The Problem: The Clinical "Shortcut" Trap
Current medical LLMs suffer from "Triage Laziness." Because they aren't penalized for missing hidden facts, they often guess a diagnosis based only on the first sentence of a patient's complaint. This is a massive **capability gap** in professional reasoning—real-world triage is an **active information discovery** problem, not a text classification problem.

We have engineered an environment that explicitly exposes this **Credit Assignment Problem**. Symptoms are locked behind diagnostic "gates"—if an agent doesn't proactively order an ECG or screen for suicidal ideation, the critical level-1 risk remains completely invisible. 

---

## 2. The Environment: The Strategic Hallway POMDP
This environment evaluates how an agent prioritized a chaotic ER Hallway under time pressure. It is built as a **Partially Observable Markov Decision Process (POMDP)**.

### What the Agent Sees & Does:
*   **Observations**: A hallway view where only raw "Chief Complaints" are visible initially. The agent must choose which of the 3 patients to assess.
*   **Actions**: The agent can `ask_symptom`, `order_test`, or `switch_patient`.
*   **State-Space Discovery**: The "hidden facts" (e.g., a hidden suicide plan or ST-Elevation) can *only* be revealed by high-utility probes.

### The Reward Signal (Rubric System):
We use a **Composable Rubric** to provide a rich, informative signal that prevents reward-hacking:
| Priority | Event | Signal | Rationale |
|---|---|---|---|
| **High** | **Triage Success** | `+0.50` | Rewards accuracy and correct care pathway. |
| **High** | **Discovery Spike** | `+0.25` | Massive reward for finding hidden critical facts. |
| **Safety**| **Repetition Wall** | `-0.20` | Terminating penalty for clinical redundancy. |
| **Operational**| **Step friction** | `-0.01` | Penalty for every wasted moment in the hallway. |
| **Gate**| **Safety Gate** | `-0.10` | Penalty for triaging without exploring first. |

---

## 3. Results: From Random Guessing to Clinical Strategy
Training our agent with GRPO fundamentally shifted its behavior from surface-level guessing to deep clinical investigation.

![Clinical Triage Progress](plot1.png)
> **Fig 1: Learning Convergence**: Our GRPO-trained agent surpasses the **3.60 Expert Heuristic baseline at Step 63**, moving from a random explore-policy to a high-utility diagnostic path.

![Behavioral Analysis](plot2.png)
> **Fig 2: Behavioral Shift**: Post-training, the agent showed an **82% reduction in "Useless Test Spam"** and a **340% increase in "High-Reward Discovery"** actions. 

![Policy Distribution Analysis](plot3.png)
> **Fig 3: Policy Stability**: Training successfully stabilized the model's behavior. Note the shift from a chaotic distribution (Red) to a high-precision cluster (Green).

---

## 4. Why It Matters: Professional Safety
This environment exists to teach LLMs a capability they current lack: **Cautious Uncertainty Handling.** 

In medical and legal domains, "Guessing is Failing." Our environment serves as a benchmark for researchers to measure how well an agent can resist shortcuts and prioritize **Safety through Evidence Gathering.** This project proves that with the right reward shaping, LLMs can learn to be disciplined clinical agents.

---

## 🚀 How to Run
```bash
# 1. Clone & Setup
git clone https://github.com/user/clinical-triage-env
pip install -r requirements.txt

# 2. Run the Strategic Hallway Benchmark
python hallway_inference.py
```

*Scenarios were refined with input from a psychiatry professor at NIMHANS to ensure medical grounding.*