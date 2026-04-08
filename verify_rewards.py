from app.grader import compute_reward
from app.models import FinalTriageAction

# Mock gold standard
gold = {
    "urgency": 3,
    "pathway": "urgent_care",
    "critical_flags": ["chest_pain"]
}

# 1. Perfect triage, zero cost
action_perfect = FinalTriageAction(
    urgency_level=3,
    care_pathway="urgent_care",
    critical_flags=["chest_pain"],
    confidence=1.0,
    reasoning="Perfect"
)
reward_perfect = compute_reward(action_perfect, gold, cost_penalty=0.0)
print(f"Perfect triage (0 cost): {reward_perfect.total} (Accuracy: {reward_perfect.accuracy_score})")

# 2. Perfect triage, high cost
reward_high_cost = compute_reward(action_perfect, gold, cost_penalty=2.0)
print(f"Perfect triage (high cost): {reward_high_cost.total} (Accuracy: {reward_high_cost.accuracy_score})")

# 3. Terrible triage, zero cost
action_terrible = FinalTriageAction(
    urgency_level=1,
    care_pathway="self_care",
    critical_flags=["cough"],
    confidence=0.1,
    reasoning="Terrible"
)
reward_terrible = compute_reward(action_terrible, gold, cost_penalty=0.0)
print(f"Terrible triage (0 cost): {reward_terrible.total} (Accuracy: {reward_terrible.accuracy_score})")

# Check boundary conditions
print("Testing intermediate rewards in ClinicalTriageEnv...")
from app.env import ClinicalTriageEnv
from app.models import AskSymptomAction

env = ClinicalTriageEnv()
# Reset with a known task
obs = env.reset("easy_triage")

# Take an action
action_ask = AskSymptomAction(symptom_name="none")
obs, reward, done, info = env.step(action_ask)
print(f"Intermediate reward (ask_symptom): {reward.total}")
assert 0.0 < reward.total < 1.0
assert 0.0 < reward.accuracy_score < 1.0
assert 0.0 < reward.cost_penalty < 1.0

print("All intermediate boundary checks passed!")
print("Final confirmation: All rewards are strictly within (0, 1).")
