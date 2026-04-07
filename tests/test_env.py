from app.env import ClinicalTriageEnv


def test_reset():
    env = ClinicalTriageEnv()
    obs = env.reset("easy_triage")
    assert obs.patient_id is not None


def test_reward_bounds():
    env = ClinicalTriageEnv()
    obs = env.reset("easy_triage")

    dummy_action = {
        "urgency_level": 3,
        "care_pathway": "GP",
        "critical_flags": [],
        "confidence": 0.5
    }

    obs, reward, done, _ = env.step(dummy_action)
    assert 0.0 <= reward.total <= 1.0