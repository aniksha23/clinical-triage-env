import random

SEED = 42
random.seed(SEED)

CASES = [
    {
        "id": "case_001",
        "age": 58,
        "symptoms": ["chest_pain", "diaphoresis", "nausea"],
        "vitals": {"bp": "90/60", "hr": 112, "temp": 37.1, "spo2": 94},
        "history": ["diabetes"],
        "presenting_complaint": "Severe chest pain for 30 minutes",
        "completeness": 1.0,
        "gold": {
            "urgency": 1,
            "pathway": "ER",
            "critical_flags": ["STEMI_risk", "hypotension"]
        }
    },
    {
        "id": "case_002",
        "age": 25,
        "symptoms": ["fever", "fatigue", "headache"],
        "vitals": {"temp": 38.5, "hr": 90, "spo2": 98},
        "history": [],
        "presenting_complaint": "Fever for 2 days",
        "completeness": 1.0,
        "gold": {
            "urgency": 4,
            "pathway": "GP",
            "critical_flags": ["infection"]
        }
    },
    {
        "id": "case_003",
        "age": 70,
        "symptoms": ["confusion", "weakness"],
        "vitals": {"bp": "100/70", "hr": 95, "spo2": 92},
        "history": ["hypertension"],
        "presenting_complaint": "Sudden confusion",
        "completeness": 0.6,
        "gold": {
            "urgency": 2,
            "pathway": "ER",
            "critical_flags": ["stroke_risk"]
        }
    }
]