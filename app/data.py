CASES = [

    # ---------------- EASY ----------------
    {
        "id": "case_001",
        "age": 58,
        "symptoms": ["chest_pain", "diaphoresis", "nausea"],
        "vitals": {"bp": "90/60", "hr": 112, "temp": 37.1, "spo2": 94},
        "history": ["diabetes"],
        "presenting_complaint": "Severe chest pain for 30 minutes",
        "completeness": 0.99,
        "gold": {
            "urgency": 1,
            "pathway": "ER",
            "critical_flags": ["chest_pain", "low_bp"],
            "priorities": {
                "chest_pain": "high",
                "bp": "high",
                "hr": "medium",
                "spo2": "medium",
                "diaphoresis": "medium",
                "nausea": "low"
            }
        }
    },
    {
        "id": "case_002",
        "age": 22,
        "symptoms": ["fever", "headache", "fatigue"],
        "vitals": {"temp": 38.2, "hr": 88, "spo2": 98},
        "history": [],
        "presenting_complaint": "Fever for 2 days",
        "completeness": 0.99,
        "gold": {
            "urgency": 4,
            "pathway": "GP",
            "critical_flags": ["fever"],
            "priorities": {
                "temp": "high",
                "fever": "high",
                "headache": "medium",
                "hr": "low",
                "fatigue": "low"
            }
        }
    },
    {
        "id": "case_003",
        "age": 30,
        "symptoms": ["cough", "sore_throat"],
        "vitals": {"temp": 37.5, "hr": 80, "spo2": 99},
        "history": [],
        "presenting_complaint": "Cold symptoms",
        "completeness": 0.99,
        "gold": {
            "urgency": 5,
            "pathway": "self_care",
            "critical_flags": [],
            "priorities": {
                "cough": "medium",
                "sore_throat": "medium",
                "temp": "low",
                "spo2": "low"
            }
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
        "completeness": 0.99,
        "gold": {
            "urgency": 2,
            "pathway": "ER",
            "critical_flags": ["low_spo2", "shortness_of_breath"],
            "priorities": {
                "spo2": "high",
                "shortness_of_breath": "high",
                "bp": "medium",
                "hr": "medium",
                "fatigue": "low"
            }
        }
    },
    {
        "id": "case_005",
        "age": 40,
        "symptoms": ["abdominal_pain", "vomiting"],
        "vitals": {"bp": "120/80", "hr": 95, "temp": 37.8},
        "history": [],
        "presenting_complaint": "Stomach pain",
        "completeness": 0.99,
        "gold": {
            "urgency": 3,
            "pathway": "urgent_care",
            "critical_flags": ["abdominal_pain"],
            "priorities": {
                "abdominal_pain": "high",
                "temp": "medium",
                "vomiting": "medium",
                "bp": "low",
                "hr": "low"
            }
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
            "critical_flags": ["high_bp", "dizziness"],
            "priorities": {
                "bp": "high",
                "dizziness": "high",
                "blurred_vision": "medium",
                "hr": "low"
            }
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
            "critical_flags": ["confusion", "weakness"],
            "priorities": {
                "confusion": "high",
                "weakness": "high",
                "bp": "high",
                "spo2": "medium",
                "hr": "low"
            }
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
            "critical_flags": ["fever", "lethargy"],
            "priorities": {
                "temp": "high",
                "lethargy": "high",
                "hr": "medium",
                "fever": "medium"
            }
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
            "critical_flags": ["chest_pain", "low_spo2"],
            "priorities": {
                "chest_pain": "high",
                "spo2": "high",
                "shortness_of_breath": "high",
                "bp": "medium",
                "hr": "medium"
            }
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
            "critical_flags": ["neck_stiffness", "fever"],
            "priorities": {
                "neck_stiffness": "high",
                "temp": "high",
                "headache": "medium",
                "hr": "medium"
            }
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
            "critical_flags": ["tachycardia"],
            "priorities": {
                "hr": "high",
                "palpitations": "medium",
                "anxiety": "low",
                "bp": "low"
            }
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
            "critical_flags": ["low_bp", "weakness"],
            "priorities": {
                "bp": "high",
                "weakness": "high",
                "hr": "medium",
                "fatigue": "low"
            }
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
            "critical_flags": ["fever", "rash"],
            "priorities": {
                "rash": "high",
                "temp": "high",
                "fever": "medium"
            }
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
            "critical_flags": ["numbness"],
            "priorities": {
                "numbness": "high",
                "back_pain": "medium",
                "bp": "low"
            }
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
            "critical_flags": ["vomiting", "dehydration"],
            "priorities": {
                "vomiting": "high",
                "bp": "high",
                "hr": "medium",
                "dehydration": "medium"
            }
        }
    },
    {
        "id": "case_016",
        "age": 68,
        "symptoms": ["chest_pain", "back_pain", "dizziness"],
        "vitals": {"bp": "170/100", "hr": 95, "spo2": 98},
        "history": ["hypertension"],
        "presenting_complaint": "Tearing chest pain",
        "completeness": 0.9,
        "gold": {
            "urgency": 1,
            "pathway": "ER",
            "critical_flags": ["chest_pain", "back_pain"],
            "priorities": {
                "chest_pain": "high",
                "back_pain": "high",
                "bp": "high",
                "hr": "medium",
                "dizziness": "low"
            }
        }
    },
    {
        "id": "case_017",
        "age": 75,
        "symptoms": ["confusion", "fever", "lethargy"],
        "vitals": {"bp": "82/50", "hr": 120, "temp": 39.2, "spo2": 92},
        "history": ["recent_surgery"],
        "presenting_complaint": "Patient is unresponsive and hot to touch",
        "completeness": 0.9,
        "gold": {
            "urgency": 1,
            "pathway": "ER",
            "critical_flags": ["confusion", "low_bp", "fever", "tachycardia"],
            "priorities": {
                "bp": "high",
                "confusion": "high",
                "temp": "high",
                "hr": "high",
                "fever": "medium",
                "lethargy": "medium"
            }
        }
    },
    {
        "id": "case_018",
        "age": 42,
        "symptoms": ["shortness_of_breath", "chest_pain", "palpitations"],
        "vitals": {"hr": 115, "spo2": 88, "bp": "Long_flight"},
        "history": ["long_flight"],
        "presenting_complaint": "Sudden breathlessness",
        "completeness": 0.9,
        "gold": {
            "urgency": 1,
            "pathway": "ER",
            "critical_flags": ["shortness_of_breath", "low_spo2", "tachycardia"],
            "priorities": {
                "spo2": "high",
                "shortness_of_breath": "high",
                "hr": "high",
                "chest_pain": "medium",
                "bp": "medium",
                "palpitations": "low"
            }
        }
    },
    {
        "id": "case_019",
        "age": 29,
        "symptoms": ["abdominal_pain", "dizziness", "nausea"],
        "vitals": {"bp": "95/55", "hr": 110},
        "history": ["missed_period"],
        "presenting_complaint": "Sharp lower abdominal pain",
        "completeness": 0.9,
        "gold": {
            "urgency": 1,
            "pathway": "ER",
            "critical_flags": ["abdominal_pain", "low_bp", "tachycardia"],
            "priorities": {
                "abdominal_pain": "high",
                "bp": "high",
                "hr": "high",
                "dizziness": "medium",
                "nausea": "low"
            }
        }
    },
    {
        "id": "case_020",
        "age": 19,
        "symptoms": ["rash", "shortness_of_breath", "swelling"],
        "vitals": {"bp": "88/45", "hr": 130, "spo2": 85},
        "history": ["peanut_allergy"],
        "presenting_complaint": "Difficulty breathing and hives",
        "completeness": 0.9,
        "gold": {
            "urgency": 1,
            "pathway": "ER",
            "critical_flags": ["rash", "shortness_of_breath", "low_bp", "low_spo2"],
            "priorities": {
                "shortness_of_breath": "high",
                "bp": "high",
                "spo2": "high",
                "hr": "high",
                "rash": "medium",
                "swelling": "medium"
            }
        }
    },
    {
        "id": "case_021",
        "age": 24,
        "symptoms": ["vomiting", "abdominal_pain", "lethargy"],
        "vitals": {"bp": "105/70", "hr": 115, "temp": 37.5, "spo2": 96},
        "history": ["type_1_diabetes"],
        "presenting_complaint": "Very tired and breathing deeply",
        "completeness": 0.9,
        "gold": {
            "urgency": 1,
            "pathway": "ER",
            "critical_flags": ["breathing_issue", "dehydration", "lethargy"],
            "priorities": {
                "lethargy": "high",
                "hr": "high",
                "abdominal_pain": "medium",
                "vomiting": "medium",
                "bp": "medium"
            }
        }
    },
    {
        "id": "case_022",
        "age": 62,
        "symptoms": ["numbness", "weakness", "dizziness"],
        "vitals": {"bp": "165/95", "hr": 80},
        "history": ["tobacco_use"],
        "presenting_complaint": "Sudden weakness in left arm that lasted 10 minutes",
        "completeness": 0.9,
        "gold": {
            "urgency": 2,
            "pathway": "ER",
            "critical_flags": ["weakness", "numbness"],
            "priorities": {
                "weakness": "high",
                "numbness": "high",
                "bp": "medium",
                "dizziness": "medium",
                "hr": "low"
            }
        }
    },
    {
        "id": "case_023",
        "age": 55,
        "symptoms": ["weakness", "dizziness", "nausea"],
        "vitals": {"bp": "100/60", "hr": 110, "spo2": 95},
        "history": ["liver_cirrhosis"],
        "presenting_complaint": "Passed black, tarry stool and feels faint",
        "completeness": 0.9,
        "gold": {
            "urgency": 2,
            "pathway": "ER",
            "critical_flags": ["weakness", "low_bp", "tachycardia"],
            "priorities": {
                "bp": "high",
                "weakness": "high",
                "hr": "high",
                "dizziness": "medium",
                "nausea": "low"
            }
        }
    },
    {
        "id": "case_024",
        "age": 12,
        "symptoms": ["abdominal_pain", "fever", "vomiting"],
        "vitals": {"temp": 38.5, "hr": 105},
        "history": [],
        "presenting_complaint": "Pain around belly button moving to lower right side",
        "completeness": 0.9,
        "gold": {
            "urgency": 3,
            "pathway": "urgent_care",
            "critical_flags": ["abdominal_pain", "fever"],
            "priorities": {
                "abdominal_pain": "high",
                "temp": "high",
                "fever": "medium",
                "vomiting": "medium",
                "hr": "low"
            }
        }
    },
    {
        "id": "case_025",
        "age": 20,
        "symptoms": ["fever", "headache", "neck_stiffness", "rash"],
        "vitals": {"temp": 39.8, "hr": 115, "bp": "100/65"},
        "history": [],
        "presenting_complaint": "Severe headache and purple spots on legs",
        "completeness": 0.9,
        "gold": {
            "urgency": 1,
            "pathway": "ER",
            "critical_flags": ["fever", "neck_stiffness", "rash", "headache"],
            "priorities": {
                "temp": "high",
                "neck_stiffness": "high",
                "rash": "high",
                "headache": "medium",
                "hr": "medium",
                "bp": "medium"
            }
        }
    }
]
