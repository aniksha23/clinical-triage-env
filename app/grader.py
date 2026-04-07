from app.models import TriageReward


def compute_reward(action, gold) -> TriageReward:
    # urgency scoring
    diff = abs(action.urgency_level - gold["urgency"])
    urgency_score = max(0.0, 1.0 - diff * 0.4)

    # pathway scoring
    pathway_score = 1.0 if action.care_pathway == gold["pathway"] else 0.0

    # flags scoring (F1-like)
    pred = set(action.critical_flags)
    true = set(gold["critical_flags"])

    if len(pred) == 0:
        flags_score = 0.0
    else:
        precision = len(pred & true) / len(pred)
        recall = len(pred & true) / len(true)
        flags_score = (precision + recall) / 2

    # penalty
    penalty = 0.0
    if len(true - pred) > 0:
        penalty = 0.2

    total = 0.4 * urgency_score + 0.35 * pathway_score + 0.25 * flags_score - penalty
    total = max(0.0, min(1.0, total))

    return TriageReward(
        total=total,
        urgency_score=urgency_score,
        pathway_score=pathway_score,
        flags_score=flags_score,
        penalty=penalty
    )