# app/data.py

SCENARIOS = [
    # 1. CARDIAC CASE (Severe accuracy penalty for missing radiation/sweating)
    {
        "id": "case_cardiac_001",
        "age": 58,
        "presenting_complaint": "Severe heaviness in my chest.",
        "demographics": {"sex": "M"},
        "history": ["diabetes", "hypertension"],
        "hidden_facts": {
            "pain_radiation": "left arm and jaw",
            "diaphoresis": True,
            "nausea": True,
            "chest_pressure": "feels like an elephant is sitting on me"
        },
        "reveal_map": {
            "pain_characterization": ["pain_radiation", "chest_pressure"],
            "associated_symptoms": ["diaphoresis", "nausea"]
        },
        "test_results": {
            "ECG": "ST elevation in leads V1-V6 (Anterior MI)",
            "BP": "95/60",
            "HR": "114",
            "SPO2": "94%"
        },
        "generic_responses": {
            "social_history": "I just want this pain to stop, doctor."
        },
        "gold": {
            "urgency": 1,
            "pathway": "ER",
            "critical_flags": ["chest_pain", "diaphoresis", "st_elevation"]
        },
        "discovery_values": {
            "ECG": 0.20, # Direct test reward
            "chest_pressure": 0.10,
            "pain_radiation": 0.05,
            "diaphoresis": 0.05
        }
    },

    # 2. SUICIDE CASE
    {
        "id": "case_mental_001",
        "age": 24,
        "presenting_complaint": "I've just been feeling really down lately.",
        "demographics": {"sex": "F"},
        "history": ["anxiety"],
        "hidden_facts": {
            "hopelessness": "I feel like there's no point to anything anymore.",
            "withdrawal": "I stopped going to work last week.",
            "suicidal_ideation": "I've been thinking about taking my whole bottle of pills tonight."
        },
        "reveal_map": {
            "mental_status_screening": ["hopelessness", "withdrawal"],
            "suicidal_ideation_screening": ["suicidal_ideation"]
        },
        "test_results": {
            "mental_status_exam": "Flat affect, avoidant eye contact.",
            "vitals": "Normal"
        },
        "gold": {
            "urgency": 1,
            "pathway": "ER",
            "critical_flags": ["suicidal_ideation", "hopelessness", "high_risk"]
        },
        "discovery_values": {
            "suicidal_ideation": 0.30,
            "mental_status_exam": 0.15, # High value for high-risk case
            "hopelessness": 0.10,
            "withdrawal": 0.05
        }
    },

    # 3. ABDOMINAL CASE
    {
        "id": "case_abdominal_001",
        "age": 35,
        "presenting_complaint": "My stomach is killing me.",
        "demographics": {"sex": "M"},
        "history": ["GERD"],
        "hidden_facts": {
            "pain_location": "lower right side",
            "rebound_tenderness": True,
            "fever": "38.5C"
        },
        "reveal_map": {
            "pain_characterization": ["pain_location"],
            "physical_exam": ["rebound_tenderness"]
        },
        "test_results": {
            "BP": "120/80",
            "HR": "98",
            "Temp": "38.5C",
            "WBC": "14.5 (Elevated)"
        },
        "gold": {
            "urgency": 2,
            "pathway": "ER",
            "critical_flags": ["appendicitis", "right_lower_quadrant_pain"]
        },
        "discovery_values": {
            "rebound_tenderness": 0.20,
            "WBC": 0.15,
            "pain_location": 0.05
        }
    }
]

# Legacy compatibility for your task system
CASES = SCENARIOS 
