from app.models import TriageReward

# --- Normalize flags (VERY IMPORTANT) ---
def normalize_flags(flags):
    """
    Converts model output flags and gold labels into a normalized set
    to handle synonyms, spacing, and casing.
    """
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


# --- Compute reward ---
def compute_reward(action, gold) -> TriageReward:
    """
    Computes weighted reward for a given agent action against the gold standard.
    Returns TriageReward(total, urgency_score, pathway_score, flags_score, penalty)
    """

    # --- Urgency score ---
    diff = abs(action.urgency_level - gold["urgency"])
    urgency_score = max(0.0, 1.0 - diff * 0.4)  # exact=1, ±1=0.6, ±2=0.2

    # --- Pathway score (slightly forgiving) ---
    pathway_score = 1.0 if action.care_pathway.lower() == gold["pathway"].lower() else 0.7 if (
        action.care_pathway in ["ER", "urgent_care"] and gold["pathway"] in ["ER", "urgent_care"]) else 0.0

    # --- Flags scoring (F1-like) ---
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

    # --- Penalty for missing critical flags ---
    missing = true - pred
    penalty = 0.1 * len(missing)  # base penalty per missed flag

    # extra penalty for highly critical symptoms
    CRITICAL = {"chest_pain", "confusion", "low_spo2"}
    if any(flag in missing for flag in CRITICAL):
        penalty += 0.2

    # --- Final total score ---
    total = 0.4 * urgency_score + 0.35 * pathway_score + 0.25 * flags_score - penalty
    total = max(0.0, min(1.0, total))  # clamp to [0,1]

    return TriageReward(
        total=total,
        urgency_score=urgency_score,
        pathway_score=pathway_score,
        flags_score=flags_score,
        penalty=penalty
    )