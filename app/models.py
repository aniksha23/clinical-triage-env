from pydantic import BaseModel, Field, RootModel
from typing import List, Literal, Optional, Dict, Union, Annotated


class PatientObservation(BaseModel):
    patient_id: str
    age: int
    presenting_complaint: str
    symptoms: Dict[str, str] = Field(default_factory=dict)
    vitals: Dict[str, str] = Field(default_factory=dict)
    observations: List[str] = Field(default_factory=list)
    history: List[str] = Field(default_factory=list)
    available_actions: List[str] = Field(default_factory=list)
    data_completeness: float = Field(default=0.005, gt=0.0, lt=1.0)


class PatientSummary(BaseModel):
    patient_id: str
    age: int
    presenting_complaint: str
    urgency_hint: str # Brief visual clue

class QueueObservation(BaseModel):
    waiting_room: List[PatientSummary]
    active_patient: Optional[PatientObservation]
    current_time_step: int

class AskSymptomAction(BaseModel):
    action_type: Literal["ask_symptom"] = "ask_symptom"
    patient_id: Optional[str] = None # Optional for legacy compatibility
    symptom_name: str

class OrderTestAction(BaseModel):
    action_type: Literal["order_test"] = "order_test"
    patient_id: Optional[str] = None # Optional for legacy compatibility
    test_name: str

class SelectPatientAction(BaseModel):
    action_type: Literal["select_patient"] = "select_patient"
    patient_id: str

class FinalTriageAction(BaseModel):
    action_type: Literal["triage"] = "triage"
    urgency_level: Literal[1, 2, 3, 4, 5]
    care_pathway: Literal["ER", "urgent_care", "GP", "self_care"]
    critical_flags: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, gt=0.0, lt=1.0)
    reasoning: Optional[str] = None

class TriageQueueItem(BaseModel):
    patient_id: str
    assigned_urgency: Literal[1, 2, 3, 4, 5]
    reasoning: str

class TriageQueueAction(BaseModel):
    action_type: Literal["submit_triage_queue"] = "submit_triage_queue"
    queue: List[TriageQueueItem]

TriageAction = Annotated[
    Union[AskSymptomAction, OrderTestAction, SelectPatientAction, FinalTriageAction, TriageQueueAction],
    Field(discriminator="action_type")
]

class TriageReward(BaseModel):
    total: float
    accuracy_score: float = 0.005
    cost_penalty: float = 0.005
    done: bool = False
    message: str = ""