from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class SafetyRequest(StrictModel):
    description: str = Field(min_length=3, max_length=5000)
    weather: str = Field(default="not provided", max_length=200)
    site_context: str = Field(default="general construction site", max_length=500)

class Finding(StrictModel):
    title: str
    severity: Literal["low", "medium", "high", "critical"]
    explanation: str
    recommended_action: str

class SafetyResponse(StrictModel):
    mode: Literal["demo", "ai"]
    summary: str
    findings: list[Finding]
    disclaimer: str

class CrackResponse(StrictModel):
    mode: Literal["demo", "ai"]
    image_received: bool
    image_filename: Optional[str] = None
    observation: str
    possible_patterns: list[str]
    recommended_next_steps: list[str]
    disclaimer: str

class PlanningRequest(StrictModel):
    area_sqft: float = Field(gt=0, le=1_000_000)
    floors: int = Field(default=1, ge=1, le=100)
    finish_level: Literal["basic", "standard", "premium"] = "standard"
    location: str = Field(default="not specified", max_length=200)

class PlanningResponse(StrictModel):
    mode: Literal["demo", "ai"]
    total_area_sqft: float
    estimated_cement_bags: int
    estimated_steel_kg: int
    indicative_cost_low_inr: int
    indicative_cost_high_inr: int
    assumptions: list[str]
    disclaimer: str

class ValuationRequest(StrictModel):
    area_sqft: float = Field(gt=0, le=1_000_000)
    rate_per_sqft_inr: float = Field(gt=0, le=1_000_000)
    age_years: int = Field(default=0, ge=0, le=200)
    condition: Literal["poor", "fair", "good", "excellent"] = "good"

class ValuationResponse(StrictModel):
    estimated_value_inr: int
    adjustment_percent: float
    assumptions: list[str]
    disclaimer: str

class AssistantRequest(StrictModel):
    question: str = Field(min_length=3, max_length=4000)
    site_context: str = Field(default="", max_length=2000)
    weather: str = Field(default="not provided", max_length=200)
