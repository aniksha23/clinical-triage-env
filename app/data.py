CASES = [

    # ---------------- EASY ----------------
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
            "critical_flags": ["chest_pain", "low_bp"]
        }
    },
    {
        "id": "case_002",
        "age": 22,
        "symptoms": ["fever", "headache", "fatigue"],
        "vitals": {"temp": 38.2, "hr": 88, "spo2": 98},
        "history": [],
        "presenting_complaint": "Fever for 2 days",
        "completeness": 1.0,
        "gold": {
            "urgency": 4,
            "pathway": "GP",
            "critical_flags": ["fever"]
        }
    },
    {
        "id": "case_003",
        "age": 30,
        "symptoms": ["cough", "sore_throat"],
        "vitals": {"temp": 37.5, "hr": 80, "spo2": 99},
        "history": [],
        "presenting_complaint": "Cold symptoms",
        "completeness": 1.0,
        "gold": {
            "urgency": 5,
            "pathway": "self_care",
            "critical_flags": []
        }
    },

    # ---------------- MEDIUM ----------------
    {
        "id": "case_004",
        "age": 65,
        "symptoms": ["shortness_of_breath", "fatigue"],
        "vitals": {"bp": "110/70", "hr": 100, "spo2": 89},
        "history": ["hypertension"],
        "presenting_complaint": "Breathlessness",
        "completeness": 1.0,
        "gold": {
            "urgency": 2,
            "pathway": "ER",
            "critical_flags": ["low_spo2", "shortness_of_breath"]
        }
    },
    {
        "id": "case_005",
        "age": 40,
        "symptoms": ["abdominal_pain", "vomiting"],
        "vitals": {"bp": "120/80", "hr": 95, "temp": 37.8},
        "history": [],
        "presenting_complaint": "Stomach pain",
        "completeness": 1.0,
        "gold": {
            "urgency": 3,
            "pathway": "urgent_care",
            "critical_flags": ["abdominal_pain"]
        }
    },
    {
        "id": "case_006",
        "age": 50,
        "symptoms": ["dizziness", "blurred_vision"],
        "vitals": {"bp": "150/95", "hr": 90},
        "history": ["hypertension"],
        "presenting_complaint": "Feeling dizzy",
        "completeness": 0.9,
        "gold": {
            "urgency": 3,
            "pathway": "urgent_care",
            "critical_flags": ["high_bp", "dizziness"]
        }
    },

    # ---------------- HARD ----------------
    {
        "id": "case_007",
        "age": 72,
        "symptoms": ["confusion", "weakness"],
        "vitals": {"bp": "100/70", "hr": 95, "spo2": 92},
        "history": ["stroke"],
        "presenting_complaint": "Sudden confusion",
        "completeness": 0.7,
        "gold": {
            "urgency": 1,
            "pathway": "ER",
            "critical_flags": ["confusion", "weakness"]
        }
    },
    {
        "id": "case_008",
        "age": 3,
        "symptoms": ["fever", "lethargy"],
        "vitals": {"temp": 39.5, "hr": 130},
        "history": [],
        "presenting_complaint": "High fever in child",
        "completeness": 0.6,
        "gold": {
            "urgency": 2,
            "pathway": "ER",
            "critical_flags": ["fever", "lethargy"]
        }
    },
    {
        "id": "case_009",
        "age": 60,
        "symptoms": ["chest_pain", "shortness_of_breath"],
        "vitals": {"bp": "140/90", "hr": 105, "spo2": 91},
        "history": ["smoker"],
        "presenting_complaint": "Chest discomfort",
        "completeness": 0.8,
        "gold": {
            "urgency": 1,
            "pathway": "ER",
            "critical_flags": ["chest_pain", "low_spo2"]
        }
    },
    {
        "id": "case_010",
        "age": 45,
        "symptoms": ["headache", "neck_stiffness"],
        "vitals": {"temp": 38.5, "hr": 100},
        "history": [],
        "presenting_complaint": "Severe headache",
        "completeness": 0.7,
        "gold": {
            "urgency": 2,
            "pathway": "ER",
            "critical_flags": ["neck_stiffness", "fever"]
        }
    },
    {
        "id": "case_011",
        "age": 28,
        "symptoms": ["palpitations", "anxiety"],
        "vitals": {"hr": 110, "bp": "120/80"},
        "history": [],
        "presenting_complaint": "Heart racing",
        "completeness": 0.9,
        "gold": {
            "urgency": 4,
            "pathway": "GP",
            "critical_flags": ["tachycardia"]
        }
    },
    {
        "id": "case_012",
        "age": 67,
        "symptoms": ["weakness", "fatigue"],
        "vitals": {"bp": "85/60", "hr": 110},
        "history": ["diabetes"],
        "presenting_complaint": "Feeling very weak",
        "completeness": 0.8,
        "gold": {
            "urgency": 1,
            "pathway": "ER",
            "critical_flags": ["low_bp", "weakness"]
        }
    },
    {
        "id": "case_013",
        "age": 35,
        "symptoms": ["rash", "fever"],
        "vitals": {"temp": 38.0},
        "history": [],
        "presenting_complaint": "Skin rash",
        "completeness": 0.9,
        "gold": {
            "urgency": 3,
            "pathway": "urgent_care",
            "critical_flags": ["fever", "rash"]
        }
    },
    {
        "id": "case_014",
        "age": 55,
        "symptoms": ["back_pain", "numbness"],
        "vitals": {"bp": "130/85"},
        "history": [],
        "presenting_complaint": "Back pain with numbness",
        "completeness": 0.7,
        "gold": {
            "urgency": 2,
            "pathway": "urgent_care",
            "critical_flags": ["numbness"]
        }
    },
    {
        "id": "case_015",
        "age": 48,
        "symptoms": ["vomiting", "dehydration"],
        "vitals": {"bp": "100/60", "hr": 105},
        "history": [],
        "presenting_complaint": "Continuous vomiting",
        "completeness": 0.8,
        "gold": {
            "urgency": 3,
            "pathway": "urgent_care",
            "critical_flags": ["vomiting", "dehydration"]
        }
    }
]