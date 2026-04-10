import difflib
from app.models import TriageReward, FinalTriageAction

# All valid canonical flag names — fuzzy matching snaps to these
CANONICAL_FLAGS = {
    "chest_pain", "low_bp", "high_bp", "tachycardia", "low_spo2",
    "shortness_of_breath", "breathing_issue", "confusion", "weakness",
    "fever", "cough", "sore_throat", "lethargy", "neck_stiffness",
    "abdominal_pain", "dizziness", "rash", "numbness", "dehydration",
    "vomiting", "palpitations", "fatigue", "headache", "back_pain",
}

ALIASES = {
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
    "fast_heart_rate": "tachycardia",
    "rapid_heart_rate": "tachycardia",
    "sob": "shortness_of_breath",
    "dyspnea": "shortness_of_breath",
    "syncope": "weakness",
    "diaphoresis": "chest_pain",  # context: usually accompanies chest pain
}


def normalize_flags(flags):
    normalized = set()
    for f in flags:
        f = f.lower().strip().replace(" ", "_")
        # 1. Try explicit alias map
        f = ALIASES.get(f, f)
        # 2. If still not canonical, try fuzzy match (cutoff 0.75 avoids false positives)
        if f not in CANONICAL_FLAGS:
            matches = difflib.get_close_matches(f, CANONICAL_FLAGS, n=1, cutoff=0.75)
            if matches:
                f = matches[0]
        normalized.add(f)
    return normalized


def compute_reward(action: FinalTriageAction, gold: dict, cost_penalty: float = 0.0) -> TriageReward:
    """
    Computes accuracy score and subtracts cumulative step costs.
    """
    # --- Urgency score ---
    diff = abs(action.urgency_level - gold["urgency"])
    urgency_score = max(0.005, min(0.995, 1.0 - diff * 0.4))

    # --- Pathway score ---
    pathway_score = 0.995 if action.care_pathway.lower() == gold["pathway"].lower() else 0.7 if (
        action.care_pathway in ["ER", "urgent_care"] and gold["pathway"] in ["ER", "urgent_care"]) else 0.005

    # --- Flags scoring ---
    pred = normalize_flags(action.critical_flags)
    true = normalize_flags(gold["critical_flags"])

    if len(pred) == 0 and len(true) == 0:
        flags_score = 0.995
    elif len(pred) == 0:
        flags_score = 0.005
    else:
        intersection = pred & true
        precision = len(intersection) / len(pred)
        recall = len(intersection) / len(true) if len(true) > 0 else 0.995
        flags_score = max(0.005, min(0.995, (precision + recall) / 2))

    # Accuracy (weighted average)
    accuracy_score = 0.4 * urgency_score + 0.35 * pathway_score + 0.25 * flags_score
    accuracy_score = max(0.005, min(0.995, accuracy_score))

    # Total score (Accuracy - Costs), clamped strictly to (0.001, 0.999)
    total = accuracy_score - cost_penalty
    total = max(0.005, min(0.995, total))

    message = f"Accuracy: {accuracy_score:.4f} | Cost: {cost_penalty:.4f}"
    if accuracy_score > 0.8:
        message += " - Excellent triage!"
    elif accuracy_score < 0.5:
        message += " - Risky triage decisions."

    return TriageReward(
        total=total,
        accuracy_score=accuracy_score,
        cost_penalty=max(0.005, min(0.995, cost_penalty)),
        done=True,
        message=message
    )