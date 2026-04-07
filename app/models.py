from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict


class PatientObservation(BaseModel):
    patient_id: str
    age: int
    symptoms: List[str]
    vitals: Dict[str, float | str]
    history: List[str]
    presenting_complaint: str
    data_completeness: float = Field(ge=0.0, le=1.0)


class TriageAction(BaseModel):
    urgency_level: Literal[1, 2, 3, 4, 5]
    care_pathway: Literal["ER", "urgent_care", "GP", "self_care"]
    critical_flags: List[str]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: Optional[str] = None


class TriageReward(BaseModel):
    total: float
    urgency_score: float
    pathway_score: float
    flags_score: float
    penalty: float