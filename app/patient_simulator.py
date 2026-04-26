import random
from typing import List, Dict, Any, Set, Optional

class PatientScenario:
    """The 'Hidden Truth' container for a specific medical case."""
    def __init__(
        self, 
        case_id: str,
        chief_complaint: str,
        demographics: Dict[str, Any],
        hidden_facts: Dict[str, Any],
        reveal_map: Dict[str, List[str]],
        test_results: Dict[str, str],
        generic_responses: Dict[str, str] = None,
        discovery_values: Dict[str, float] = None
    ):
        self.case_id = case_id
        self.chief_complaint = chief_complaint
        self.demographics = demographics
        self.hidden_facts = hidden_facts
        self.reveal_map = reveal_map
        self.test_results = test_results
        self.generic_responses = generic_responses or {}
        self.discovery_values = discovery_values or {}

class PatientSimulator:
    def __init__(self, scenario: PatientScenario):
        self.scenario = scenario
        self.revealed_facts: Set[str] = set()
        self.observations: List[str] = []
        self.questions_history: List[str] = []
        self.tests_done: List[str] = []
        self.irritation_level = 0
        self.max_patience = 12
        self.last_step_ig = 0.0

    def _normalize_query(self, query: str) -> str:
        query = query.lower().strip().replace(" ", "_")
        mapping = {
            "abdominal_pain_location": "pain_characterization",
            "abdominal_pain_character": "pain_characterization",
            "chest_pain_type": "pain_characterization",
            "sweating": "associated_symptoms",
            "nausea": "associated_symptoms",
            "suicidal_thoughts": "suicidal_ideation_screening",
            "mood": "mental_status_screening",
        }
        return mapping.get(query, query)

    def handle_question(self, question_type: str) -> str:
        self.last_step_ig = 0.0
        question_type = self._normalize_query(question_type)
        self.questions_history.append(question_type)
        self.irritation_level += 1

        if self.questions_history.count(question_type) > 1:
            return "Patient looks annoyed: 'I already told you about that.'"

        if self.irritation_level > self.max_patience:
            return "Patient seems exhausted and less responsive."

        response_segments = []
        ig_accumulated = 0.0
        
        def process_fact(f):
            nonlocal ig_accumulated
            if f in self.scenario.hidden_facts and f not in self.revealed_facts:
                response_segments.append(self._format_fact(f))
                self.revealed_facts.add(f)
                self._add_observation_for_fact(f)
                # Value of Information: Only reward if defined as an important finding
                ig_accumulated += self.scenario.discovery_values.get(f, 0.0)

        if question_type == "suicidal_ideation_screening":
            process_fact("suicidal_ideation")
        elif question_type in self.scenario.reveal_map:
            for fact in self.scenario.reveal_map[question_type]:
                if fact == "suicidal_ideation": continue
                process_fact(fact)

        self.last_step_ig = ig_accumulated
        if not response_segments:
            return self._generic_response(question_type)
        return " ".join(response_segments)

    def handle_test(self, test_name: str) -> str:
        self.last_step_ig = 0.0
        self.tests_done.append(test_name)
        self.irritation_level += 1
        if test_name in self.scenario.test_results:
            if test_name not in self.revealed_facts:
                self.revealed_facts.add(test_name)
                # No reward for irrelevant tests (zeros out participation trophy)
                self.last_step_ig = self.scenario.discovery_values.get(test_name, 0.0)
            return self.scenario.test_results[test_name]
        return "Test results normal."

    def _format_fact(self, fact: str) -> str:
        value = self.scenario.hidden_facts.get(fact)
        templates = {
            "pain_radiation": f"The pain spreads to my {value}.",
            "diaphoresis": "I've been sweating a lot and feeling cold.",
            "hopelessness": "I just feel like nothing matters anymore, you know?",
            "suicidal_ideation": "I... I've been thinking about ending it. I have a plan.",
            "nausea": "I feel like I'm going to throw up.",
        }
        return templates.get(fact, str(value))

    def _generic_response(self, question_type: str) -> str:
        default_map = {
            "mental_status_screening": "I feel okay, just tired I guess.",
            "pain_characterization": "It's just... pain.",
        }
        return self.scenario.generic_responses.get(question_type, default_map.get(question_type, "I'm not sure."))

    def _add_observation_for_fact(self, fact: str):
        obs_map = {
            "diaphoresis": "Patient is visibly pale and clammy.",
            "hopelessness": "Patient avoids eye contact and speaks in a flat tone.",
        }
        if fact in obs_map and obs_map[fact] not in self.observations:
            self.observations.append(obs_map[fact])

    def get_current_observations(self) -> List[str]:
        return self.observations
