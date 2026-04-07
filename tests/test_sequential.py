import pytest
from app.env import ClinicalTriageEnv
from app.models import AskSymptomAction, OrderTestAction, FinalTriageAction

def test_sequential_flow():
    env = ClinicalTriageEnv()
    
    # 1. Reset
    obs = env.reset("easy_triage")
    assert obs.patient_id is not None
    assert len(obs.vitals) == 1
    assert len(obs.symptoms) == 0
    
    # 2. Ask Symptom
    action = AskSymptomAction(symptom_name="chest_pain")
    obs, reward, done, _ = env.step(action)
    
    assert "chest_pain" in obs.symptoms
    assert reward.cost_penalty == 0.05
    assert not done
    
    # 3. Order Test
    action = OrderTestAction(test_name="bp")
    obs, reward, done, _ = env.step(action)
    
    assert "bp" in obs.vitals
    assert reward.cost_penalty == pytest.approx(0.15) # 0.05 + 0.1
    assert not done
    
    # 4. Final Triage
    action = FinalTriageAction(
        urgency_level=1,
        care_pathway="ER",
        critical_flags=["chest_pain", "low_bp"],
        confidence=0.9,
        reasoning="Patient has chest pain and low blood pressure."
    )
    obs, reward, done, _ = env.step(action)
    
    assert done
    assert reward.accuracy_score > 0
    assert reward.total == reward.accuracy_score - reward.cost_penalty

def test_invalid_state():
    env = ClinicalTriageEnv()
    obs = env.reset("easy_triage")
    
    action = FinalTriageAction(urgency_level=3, care_pathway="GP", confidence=0.5)
    env.step(action)
    
    # Stepping after done should raise error
    with pytest.raises(RuntimeError):
        env.step(action)

if __name__ == "__main__":
    pytest.main([__file__])
