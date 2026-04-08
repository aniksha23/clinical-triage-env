from pydantic import BaseModel, Field, RootModel
from typing import List, Literal, Optional, Dict, Union, Annotated


class PatientObservation(BaseModel):
    patient_id: str
    age: int
    presenting_complaint: str
    symptoms: Dict[str, bool] = Field(default_factory=dict)
    vitals: Dict[str, float | str] = Field(default_factory=dict)
    history: List[str] = Field(default_factory=list)
    available_actions: List[str] = Field(default_factory=list)
    data_completeness: float = Field(default=0.01, ge=0.0, le=1.0)


class AskSymptomAction(BaseModel):
    action_type: Literal["ask_symptom"] = "ask_symptom"
    symptom_name: str


class OrderTestAction(BaseModel):
    action_type: Literal["order_test"] = "order_test"
    test_name: str


class FinalTriageAction(BaseModel):
    action_type: Literal["triage"] = "triage"
    urgency_level: Literal[1, 2, 3, 4, 5]
    care_pathway: Literal["ER", "urgent_care", "GP", "self_care"]
    critical_flags: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: Optional[str] = None


TriageAction = Annotated[
    Union[AskSymptomAction, OrderTestAction, FinalTriageAction],
    Field(discriminator="action_type")
]


class TriageReward(BaseModel):
    total: float
    accuracy_score: float = 0.01
    cost_penalty: float = 0.01
    done: bool = False
    message: str = ""