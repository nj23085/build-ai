import os
from typing import Any

DISCLAIMER = (
    "Advisory only. This output is not a substitute for a qualified engineer, "
    "site safety officer, quantity surveyor, or licensed property valuer."
)

def _ai_enabled() -> bool:
    return os.getenv("AI_PROVIDER", "demo").lower() == "gemini" and bool(os.getenv("GEMINI_API_KEY"))

def _gemini_generate(prompt: str, image_bytes: bytes | None = None, mime_type: str | None = None) -> str:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    contents: list[Any] = [prompt]
    if image_bytes and mime_type:
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=contents,
        config=types.GenerateContentConfig(temperature=0.2),
    )
    return response.text or "No text response was returned."

def analyze_safety(description: str, weather: str, site_context: str) -> dict:
    if _ai_enabled():
        prompt = (
            "You are a cautious construction safety assistant. Analyze the following site description. "
            "Return concise plain text with a summary and findings; each finding must include severity "
            "(low/medium/high/critical), explanation, and recommended action. Do not claim certainty "
            "from incomplete information. Description: " + description +
            "\nWeather: " + weather + "\nSite context: " + site_context
        )
        try:
            text = _gemini_generate(prompt)
            return {"mode": "ai", "summary": text[:1800], "findings": [
                {"title": "AI advisory — verify on site", "severity": "medium",
                 "explanation": text[:1200], "recommended_action": "Have the site safety officer verify findings and implement applicable controls."}
            ], "disclaimer": DISCLAIMER}
        except Exception:
            pass
    lower = description.lower()
    findings = []
    checks = [
        (["edge", "height", "roof", "scaffold", "fall"], "Fall hazard", "high",
         "Potential fall exposure was mentioned.", "Stop access to exposed edges and verify guardrails, platforms and appropriate fall protection."),
        (["helmet", "ppe", "without harness", "no gloves", "no goggles"], "PPE concern", "medium",
         "The description suggests missing or inadequate protective equipment.", "Pause the affected task and verify task-specific PPE is available and correctly used."),
        (["wire", "electric", "cable", "live"], "Electrical hazard", "high",
         "Electrical equipment or wiring was mentioned.", "Isolate the area and have an authorized electrician inspect it."),
        (["rain", "storm", "wind", "lightning"], "Weather-related risk", "medium",
         "Weather may affect lifting, access, visibility or surface conditions.", "Follow the site weather plan and stop activities when site rules or manufacturer limits require it."),
    ]
    for terms, title, severity, explanation, action in checks:
        if any(term in lower for term in terms) or (title == "Weather-related risk" and any(x in weather.lower() for x in ["rain", "storm", "wind", "lightning"])):
            findings.append({"title": title, "severity": severity, "explanation": explanation, "recommended_action": action})
    if not findings:
        findings.append({"title": "General site review", "severity": "low",
                         "explanation": "The demo checker found no specific keyword-triggered hazard; this does not mean the site is safe.",
                         "recommended_action": "Complete the approved site-specific risk assessment and inspect the work area in person."})
    return {"mode": "demo", "summary": "Preliminary screening based on the supplied text; inspect the site and verify all controls.", "findings": findings, "disclaimer": DISCLAIMER}

def analyze_crack(image_bytes: bytes, filename: str, mime_type: str, description: str) -> dict:
    if _ai_enabled():
        prompt = (
            "You are a cautious construction observation assistant. Review the attached image and description. "
            "Do not diagnose structural safety from an image alone. Describe visible observations, possible "
            "crack patterns only if visible, uncertainty, and recommended next steps. Description: " + (description or "None supplied")
        )
        try:
            text = _gemini_generate(prompt, image_bytes, mime_type)
            return {"mode": "ai", "image_received": True, "image_filename": filename,
                    "observation": text[:2500],
                    "possible_patterns": ["AI-generated visual observation; confirm with a qualified professional"],
                    "recommended_next_steps": ["Record crack width, length, location and date.", "Photograph with a scale and repeat measurements.", "Arrange inspection by a qualified structural engineer, especially for widening, diagonal, or load-bearing-area cracks."],
                    "disclaimer": DISCLAIMER}
        except Exception:
            pass
    return {"mode": "demo", "image_received": True, "image_filename": filename,
            "observation": "Image upload received. Demo mode does not inspect image pixels; add a Gemini API key for multimodal visual observations.",
            "possible_patterns": ["Not determined in demo mode"],
            "recommended_next_steps": ["Record the crack's location, width, length and date.", "Photograph with a ruler or crack gauge for scale.", "Ask a qualified structural engineer to inspect concerning or changing cracks."],
            "disclaimer": DISCLAIMER}

def estimate_planning(area_sqft: float, floors: int, finish_level: str, location: str) -> dict:
    total = area_sqft * floors
    # Deliberately rough educational assumptions, not a bill of quantities.
    cement = round(total * 0.40)
    steel = round(total * 3.5)
    rate = {"basic": 1500, "standard": 2100, "premium": 3000}[finish_level]
    base = total * rate
    return {"mode": "demo", "total_area_sqft": round(total, 2),
            "estimated_cement_bags": cement, "estimated_steel_kg": steel,
            "indicative_cost_low_inr": round(base * 0.85),
            "indicative_cost_high_inr": round(base * 1.20),
            "assumptions": [
                "Illustrative thumb-rule quantities only; structural design and drawings are not included.",
                f"Finish level: {finish_level}; location entered: {location}. Local rates can differ materially.",
                "Validate quantities, specifications, taxes, labour and contingency with a qualified estimator."
            ], "disclaimer": DISCLAIMER}

def estimate_valuation(area_sqft: float, rate_per_sqft_inr: float, age_years: int, condition: str) -> dict:
    condition_adjust = {"poor": -0.20, "fair": -0.10, "good": 0.0, "excellent": 0.08}[condition]
    age_adjust = min(age_years * 0.01, 0.40)
    adjustment = max(-0.50, min(0.15, condition_adjust - age_adjust))
    value = area_sqft * rate_per_sqft_inr * (1 + adjustment)
    return {"estimated_value_inr": round(value), "adjustment_percent": round(adjustment * 100, 2),
            "assumptions": ["Uses the user-provided rate per square foot.", "Age/condition adjustment is a simple illustrative model, not a market appraisal."],
            "disclaimer": DISCLAIMER}


def answer_assistant(question: str, site_context: str, weather: str) -> dict:
    if _ai_enabled():
        prompt = (
            "You are a practical construction knowledge assistant. "
            "Give specific, concise, cautious advice. For work at height, cover "
            "risk assessment, safe access/platforms, edge protection, fall "
            "protection, equipment inspection, weather, training and rescue planning. "
            "Do not certify safety or replace local rules or qualified professionals.\n"
            f"Question: {question}\n"
            f"Site context: {site_context}\n"
            f"Weather: {weather}"
        )
        try:
            return {
                "mode": "ai",
                "answer": _gemini_generate(prompt)[:3000],
                "disclaimer": DISCLAIMER,
            }
        except Exception:
            pass

    q = question.lower()

    if any(w in q for w in [
        "work at height", "working at height", "height work",
        "fall protection", "roof work", "scaffold", "ladder",
        "working on a roof", "working above ground",
    ]):
        answer = (
            "Before work at height: (1) complete the task-specific risk "
            "assessment and use a safer ground-level method where feasible; "
            "(2) verify safe access and a suitable, inspected platform or "
            "scaffold; (3) check guardrails, toe boards and protected openings; "
            "(4) where collective protection cannot control the risk, use the "
            "approved fall-protection system with compatible, inspected equipment "
            "and suitable anchorage; (5) ensure workers are trained and authorized; "
            "(6) check wind, rain, lighting and surface conditions; and "
            "(7) have an emergency/rescue plan before starting. Keep people away "
            "from the area below. Follow local regulations and the site safety plan; "
            "a checklist alone does not establish that the work is safe."
        )
    elif any(w in q for w in [
        "crack", "structural", "foundation", "beam", "column",
    ]):
        answer = (
            "Record the location, length, width, date and any change over time. "
            "Photograph the area with a scale. Restrict access if there are signs "
            "of significant movement or distress and request inspection by a "
            "qualified structural engineer. Do not infer structural safety from "
            "a photo or chatbot response."
        )
    elif any(w in q for w in [
        "rain", "weather", "wind", "storm", "lightning",
    ]):
        answer = (
            f"Review the site weather plan and equipment/manufacturer limits. "
            f"Weather supplied: {weather}. Reassess access, lifting, electrical "
            "work and exposed surfaces; suspend affected tasks when site rules "
            "or safe operating limits require it."
        )
    elif any(w in q for w in [
        "concrete", "cement", "curing", "mix design",
    ]):
        answer = (
            "Follow the approved mix design, project specification and applicable "
            "standards. Verify material quality, placement conditions and curing "
            "method/duration with the responsible engineer. Do not use a generic "
            "chat response as a substitute for project-specific instructions."
        )
    elif any(w in q for w in [
        "ppe", "helmet", "safety", "hazard", "protective equipment",
    ]):
        answer = (
            "Start with the task-specific risk assessment. Eliminate hazards where "
            "possible, then use engineering and administrative controls and "
            "task-appropriate PPE. Verify safe access, exclusion zones, equipment "
            "condition and worker training. Report immediate danger to the site "
            "supervisor and follow the site's emergency procedures."
        )
    else:
        answer = (
            "Please include the specific task, material or system, site conditions "
            "and relevant project specification so I can give a more focused "
            "demo response. Verify recommendations against approved drawings, "
            "site procedures and qualified professional advice."
        )

    return {
        "mode": "demo",
        "answer": answer,
        "disclaimer": DISCLAIMER,
    }
