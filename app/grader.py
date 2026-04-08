from app.models import TriageReward, FinalTriageAction


def normalize_flags(flags):
    mapping = {
        "low bp": "low_bp",
        "bp_low": "low_bp",
        "high bp": "high_bp",
        "high heart rate": "tachycardia",
        "high hr": "tachycardia",
        "low spo2": "low_spo2",
        "shortness of breath": "shortness_of_breath",
        "severe_chest_pain": "chest_pain",
        "cardiac": "chest_pain",
        "heart_pain": "chest_pain",
        "hypotension": "low_bp",
        "respiratory": "breathing_issue",
        "confusion": "confusion",
        "weakness": "weakness",
        "fever": "fever",
        "cough": "cough",
        "sore_throat": "sore_throat"
    }
    normalized = set()
    for f in flags:
        f = f.lower().strip().replace(" ", "_")
        f = mapping.get(f, f)
        normalized.add(f)
    return normalized


def compute_reward(action: FinalTriageAction, gold: dict, cost_penalty: float = 0.0) -> TriageReward:
    """
    Computes accuracy score and subtracts cumulative step costs.
    """
    # --- Urgency score ---
    diff = abs(action.urgency_level - gold["urgency"])
    urgency_score = max(0.0, 1.0 - diff * 0.4)

    # --- Pathway score ---
    pathway_score = 1.0 if action.care_pathway.lower() == gold["pathway"].lower() else 0.7 if (
        action.care_pathway in ["ER", "urgent_care"] and gold["pathway"] in ["ER", "urgent_care"]) else 0.0

    # --- Flags scoring ---
    pred = normalize_flags(action.critical_flags)
    true = normalize_flags(gold["critical_flags"])

    if len(pred) == 0 and len(true) == 0:
        flags_score = 1.0
    elif len(pred) == 0:
        flags_score = 0.0
    else:
        intersection = pred & true
        precision = len(intersection) / len(pred)
        recall = len(intersection) / len(true) if len(true) > 0 else 1.0
        flags_score = (precision + recall) / 2

    # Accuracy (weighted average)
    accuracy_score = 0.4 * urgency_score + 0.35 * pathway_score + 0.25 * flags_score

    # Total score (Accuracy - Costs), clamped strictly to (0, 1)
    total = accuracy_score - cost_penalty
    total = max(0.01, min(0.99, total))

    message = f"Accuracy: {accuracy_score:.2f} | Cost: {cost_penalty:.2f}"
    if accuracy_score > 0.8:
        message += " - Excellent triage!"
    elif accuracy_score < 0.5:
        message += " - Risky triage decisions."

    return TriageReward(
        total=total,
        accuracy_score=accuracy_score,
        cost_penalty=cost_penalty,
        done=True,
        message=message
    )