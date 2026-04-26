# app/queue_grader.py
from typing import List, Dict, Any
from app.models import TriageQueueAction

def compute_queue_reward(action: TriageQueueAction, ground_truth: Dict[str, Any]) -> float:
    """
    Grades a Triage Queue based on sorting order and urgency assignment.
    ground_truth: { patient_id: { "gold": { "urgency": int } } }
    """
    total_score = 0.0
    queue = action.queue
    num_patients = len(queue)
    
    if num_patients == 0:
        return 0.005

    # 1. Individual Urgency Matching (40% of score)
    match_score = 0
    for item in queue:
        p_id = item.patient_id
        if p_id in ground_truth:
            true_urgency = ground_truth[p_id]["gold"]["urgency"]
            diff = abs(item.assigned_urgency - true_urgency)
            match_score += max(0, 1.0 - (diff * 0.3))
    
    match_score /= num_patients
    
    # 2. Priority Sorting Order (60% of score)
    # Patients at the start of the list are 'treated first'
    # Score decreases if a high-urgency patient is placed late in the list.
    order_score = 1.0
    
    # Get all true urgencies to find the "Top Crisis"
    true_urgencies = {p_id: data["gold"]["urgency"] for p_id, data in ground_truth.items()}
    critical_p_ids = [p_id for p_id, urg in true_urgencies.items() if urg == 1]
    
    # CRITICAL RULE: If a Level 1 exists, it MUST be in the top 2 slots.
    if critical_p_ids:
        top_ids = [item.patient_id for item in queue[:2]]
        if not any(cid in top_ids for cid in critical_p_ids):
            # Clinical Failure: Let a L1 patient wait while seeing 2+ non-L1 patients
            order_score *= 0.2 

    # Inversion Penalty: Penalty every time a less-urgent patient is before a more-urgent one
    inversions = 0
    max_inversions = (num_patients * (num_patients - 1)) / 2
    
    for i in range(len(queue)):
        for j in range(i + 1, len(queue)):
            p_i = queue[i].patient_id
            p_j = queue[j].patient_id
            
            if p_i in true_urgencies and p_j in true_urgencies:
                # TRUE urgency: 1 is higher than 5.
                # So if i is at the top (i < j), then urgency_i should be <= urgency_j
                if true_urgencies[p_i] > true_urgencies[p_j]:
                    inversions += 1
    
    inversion_penalty = (inversions / max_inversions) if max_inversions > 0 else 0
    order_score *= (1.0 - inversion_penalty)

    # Final Combined Score
    final_score = (0.4 * match_score + 0.6 * order_score)
    return max(0.005, min(0.995, final_score))
