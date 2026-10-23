
import logging
import os
from typing import Any

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

DISCLAIMER = (
    "Advisory only. This output is not a substitute for a qualified engineer, "
    "site safety officer, quantity surveyor, or licensed property valuer."
)


def _ai_enabled() -> bool:
    return (
        os.getenv("AI_PROVIDER", "demo").strip().lower() == "gemini"
        and bool(os.getenv("GEMINI_API_KEY", "").strip())
    )


def _gemini_generate(
    prompt: str,
    image_bytes: bytes | None = None,
    mime_type: str | None = None,
) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Gemini API key is not configured.")

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    client = genai.Client(api_key=api_key)

    contents: list[Any] = [prompt]
    if image_bytes is not None:
        if not mime_type:
            raise ValueError("Image MIME type is required.")
        contents.append(
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        )

    response = client.models.generate_content(
        model=model,
        contents=contents,
    )
    text = getattr(response, "text", None)
    if not text or not text.strip():
        raise RuntimeError("Gemini returned an empty response.")

    return text.strip()


def _log_gemini_failure(workflow: str, exc: Exception) -> None:
    """Log safe Gemini diagnostics without credentials or request contents."""
    status_code = getattr(exc, "status_code", None)
    error_type = type(exc).__name__

    # Log only the exception class and numeric HTTP status.
    # Do not log exception messages, which may contain sensitive details.
    logger.warning(
        "Gemini request failed; workflow=%s error_type=%s status_code=%s",
        workflow,
        error_type,
        status_code if isinstance(status_code, int) else "unknown",
    )

def analyze_safety(description: str, weather: str, site_context: str) -> dict:
    if _ai_enabled():
        prompt = (
            "You are a cautious construction site safety assistant. "
            "Assess the described observation, identify hazards and practical "
            "controls, and state uncertainties. Do not claim to certify safety. "
            f"Observation: {description}\n"
            f"Weather: {weather}\n"
            f"Site context: {site_context}"
        )
        try:
            text = _gemini_generate(prompt)
            return {
                "mode": "ai",
                "risk_level": "Review required",
                "summary": text[:2500],
                "recommended_controls": [
                    "Have a competent site supervisor verify the hazards and controls.",
                    "Stop work and isolate the area if an immediate serious hazard exists.",
                ],
                "disclaimer": DISCLAIMER,
            }
        except Exception as exc:
            _log_gemini_failure("safety", exc)

    return {
        "mode": "demo",
        "risk_level": "Review required",
        "summary": (
            "Demo screening only. Review the observation, site conditions, "
            "and existing controls with a competent site supervisor."
        ),
        "recommended_controls": [
            "Identify hazards and assess the risks before work begins.",
            "Use suitable controls and verify that workers understand them.",
            "Stop work and isolate the area if an immediate serious hazard exists.",
        ],
        "disclaimer": DISCLAIMER,
    }


def analyze_crack(
    image_bytes: bytes,
    filename: str,
    mime_type: str,
    description: str,
) -> dict:
    if _ai_enabled():
        prompt = (
            "You are a cautious construction observation assistant. Review the "
            "attached image and description. Describe only features actually "
            "visible in the image, including apparent crack location, direction, "
            "and pattern where discernible. State uncertainty and image limitations. "
            "Do not diagnose structural safety or infer crack depth from the image. "
            "Recommend appropriate next steps. Description: "
            + (description or "None supplied")
        )
        try:
            text = _gemini_generate(prompt, image_bytes, mime_type)
            return {
                "mode": "ai",
                "image_received": True,
                "image_filename": filename,
                "observation": text[:2500],
                "possible_patterns": [
                    "AI-generated visual observation; confirm with a qualified professional"
                ],
                "recommended_next_steps": [
                    "Record crack width, length, location and date.",
                    "Photograph with a scale and repeat measurements.",
                    "Arrange inspection by a qualified structural engineer, especially for widening, diagonal, or load-bearing-area cracks.",
                ],
                "disclaimer": DISCLAIMER,
            }
        except Exception as exc:
            _log_gemini_failure("crack_analysis", exc)

    return {
        "mode": "demo",
        "image_received": True,
        "image_filename": filename,
        "observation": (
            "Image upload received. Demo mode does not inspect image pixels; "
            "configure a valid Gemini API key and model access for multimodal "
            "visual observations."
        ),
        "possible_patterns": ["Not determined in demo mode"],
        "recommended_next_steps": [
            "Record the crack's location, width, length and date.",
            "Photograph with a ruler or crack gauge for scale.",
            "Ask a qualified structural engineer to inspect concerning or changing cracks.",
        ],
        "disclaimer": DISCLAIMER,
    }


def estimate_planning(
    area_sqft: float,
    floors: int,
    finish_level: str,
    location: str,
) -> dict:
    area = max(float(area_sqft), 0.0) * max(int(floors), 1)
    rates = {
        "basic": (1200, 1600),
        "standard": (1785, 2520),
        "premium": (2500, 3500),
    }
    finish = (finish_level or "standard").strip().lower()
    low_rate, high_rate = rates.get(finish, rates["standard"])

    # Illustrative planning assumptions, not a quantity-surveyor takeoff.
    cement_bags = round(area * 0.4)
    steel_kg = round(area * 3.5)

    return {
        "mode": "demo",
        "area_sqft": round(area, 2),
        "location": location,
        "finish_level": finish,
        "estimated_cement_bags": cement_bags,
        "estimated_steel_kg": steel_kg,
        "estimated_cost_low_inr": round(area * low_rate),
        "estimated_cost_high_inr": round(area * high_rate),
        "disclaimer": (
            "Illustrative estimate only. Validate quantities, structural design, "
            "local rates, taxes, and site conditions with qualified professionals."
        ),
    }


def estimate_valuation(
    area_sqft: float,
    rate_per_sqft_inr: float,
    age_years: float,
    condition: str,
) -> dict:
    area = max(float(area_sqft), 0.0)
    rate = max(float(rate_per_sqft_inr), 0.0)
    age = max(float(age_years), 0.0)

    condition_factor = {
        "excellent": 1.0,
        "good": 0.9,
        "fair": 0.8,
        "poor": 0.65,
    }.get((condition or "fair").strip().lower(), 0.8)

    age_factor = max(0.5, 1.0 - min(age, 100.0) * 0.005)
    estimated_value = area * rate * condition_factor * age_factor

    return {
        "mode": "demo",
        "area_sqft": round(area, 2),
        "rate_per_sqft_inr": round(rate, 2),
        "age_years": round(age, 2),
        "condition": condition,
        "estimated_value_inr": round(estimated_value),
        "disclaimer": (
            "Illustrative formula only, not a professional valuation or "
            "a substitute for comparable sales and a licensed valuer."
        ),
    }


def answer_assistant(
    question: str,
    site_context: str,
    weather: str,
) -> dict:
    if _ai_enabled():
        prompt = (
            "You are a cautious construction site assistant. Give practical, "
            "clear guidance, highlight important safety controls, acknowledge "
            "uncertainty, and recommend qualified professional review when needed. "
            f"Question: {question}\n"
            f"Site context: {site_context}\n"
            f"Weather: {weather}"
        )
        try:
            text = _gemini_generate(prompt)
            return {
                "mode": "ai",
                "answer": text[:3000],
                "disclaimer": DISCLAIMER,
            }
        except Exception as exc:
            _log_gemini_failure("assistant", exc)

    q = (question or "").lower()

    if any(term in q for term in ["height", "edge", "harness", "scaffold", "fall"]):
        answer = (
            "Before work at height, assess the fall risk and use a suitable, "
            "inspected work platform or scaffold with guardrails where practicable. "
            "Provide appropriate fall protection, safe access, worker training, "
            "weather checks, and a rescue plan. Secure tools and materials, keep "
            "people clear of the area below, and stop work if conditions are unsafe. "
            "A competent person must verify the site-specific controls."
        )
    elif any(term in q for term in ["crack", "structural", "column", "beam", "foundation"]):
        answer = (
            "Document the defect's location, direction, length, and measured width. "
            "Photograph it with a scale and check whether it changes over time. "
            "Do not infer structural safety from a photograph alone. Escalate "
            "widening cracks, displaced surfaces, or cracks near structural members "
            "to a qualified structural engineer."
        )
    elif any(term in q for term in ["weather", "rain", "wind", "storm", "lightning"]):
        answer = (
            "Check the current forecast and site conditions before work. Assess "
            "slippery access, water accumulation, wind effects on lifting and work "
            "at height, and lightning exposure. Suspend affected activities when "
            "site controls or manufacturer limits cannot be maintained."
        )
    elif any(term in q for term in ["concrete", "curing", "pour", "cement"]):
        answer = (
            "Verify the approved mix, formwork, reinforcement, access, and pour "
            "sequence before placement. Use required PPE, control wet-concrete "
            "skin and eye exposure, and follow the project specification for "
            "compaction, sampling, curing, and strength verification."
        )
    else:
        answer = (
            "Complete a task-specific risk assessment, confirm worker competence "
            "and required PPE, inspect equipment and access, maintain housekeeping, "
            "and verify emergency arrangements. Follow the approved method statement "
            "and applicable site procedures; stop and escalate any serious hazard."
        )

    return {
        "mode": "demo",
        "answer": answer,
        "disclaimer": DISCLAIMER,
    }
