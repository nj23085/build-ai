import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from .schemas import (
    SafetyRequest, SafetyResponse, CrackResponse, PlanningRequest, PlanningResponse,
    ValuationRequest, ValuationResponse, AssistantRequest
)
from .services import analyze_safety, analyze_crack, estimate_planning, estimate_valuation, answer_assistant

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
app = FastAPI(title="Multimodal Construction Intelligence Platform API", version="1.0.0",
              description="Construction advisory MVP with demo mode and optional Gemini multimodal integration.")

origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"name": "Multimodal Construction Intelligence Platform", "docs": "/docs", "health": "/health"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "construction-intelligence-api"}

@app.post("/api/analyze/safety", response_model=SafetyResponse)
def safety(payload: SafetyRequest):
    return analyze_safety(payload.description, payload.weather, payload.site_context)

@app.post("/api/analyze/cracks", response_model=CrackResponse)
async def cracks(image: UploadFile = File(...), description: str = Form("")):
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if image.content_type not in allowed:
        raise HTTPException(status_code=415, detail="Upload a JPG, PNG or WEBP image.")
    max_mb = int(os.getenv("MAX_UPLOAD_MB", "8"))
    data = await image.read(max_mb * 1024 * 1024 + 1)
    if not data:
        raise HTTPException(status_code=400, detail="The uploaded image is empty.")
    if len(data) > max_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Image exceeds the {max_mb} MB limit.")
    return analyze_crack(data, image.filename or "uploaded-image", image.content_type, description)

@app.post("/api/planning/estimate", response_model=PlanningResponse)
def planning(payload: PlanningRequest):
    return estimate_planning(payload.area_sqft, payload.floors, payload.finish_level, payload.location)

@app.post("/api/valuation/estimate", response_model=ValuationResponse)
def valuation(payload: ValuationRequest):
    return estimate_valuation(payload.area_sqft, payload.rate_per_sqft_inr, payload.age_years, payload.condition)

@app.post("/api/assistant",)
def assistant(payload: AssistantRequest):
    return answer_assistant(payload.question, payload.site_context, payload.weather)
