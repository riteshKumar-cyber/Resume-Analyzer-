import json
import re
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

from config import settings
from utils.helpers import logger, GeminiAnalysisError


class ResumeAnalysisResponse(BaseModel):
    """Pydantic model for structured Resume Analysis response."""
    ats_score: int = Field(description="ATS compatibility score from 0 to 100", ge=0, le=100)
    summary: str = Field(description="Executive summary of candidate profile")
    technical_skills: List[str] = Field(default_factory=list, description="Technical skills extracted")
    soft_skills: List[str] = Field(default_factory=list, description="Soft skills extracted")
    missing_skills: List[str] = Field(default_factory=list, description="Missing key industry skills")
    strengths: List[str] = Field(default_factory=list, description="Key strengths found in resume")
    weaknesses: List[str] = Field(default_factory=list, description="Areas of weakness or lack of impact")
    improvement_suggestions: List[str] = Field(default_factory=list, description="Actionable improvement suggestions")
    grammar_suggestions: List[str] = Field(default_factory=list, description="Grammar, phrasing, and formatting fixes")
    recommended_roles: List[str] = Field(default_factory=list, description="Best suitable job roles for candidate")
    experience_level: str = Field(description="Experience level e.g. Entry, Junior, Mid, Senior, Executive")
    career_roadmap: List[str] = Field(default_factory=list, description="Step-by-step career growth roadmap")
    interview_prep_tips: List[str] = Field(default_factory=list, description="Targeted interview preparation tips")


class GeminiService:
    """Service interacting with Google Gemini API for resume analysis."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None

    def _get_client(self) -> genai.Client:
        """Lazy initialization of Google GenAI Client."""
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            logger.error("GEMINI_API_KEY is missing or unconfigured.")
            raise GeminiAnalysisError(
                "Gemini API key is not configured. Please set a valid GEMINI_API_KEY in your .env file."
            )
        
        if self.client is None:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Client: {str(e)}")
                raise GeminiAnalysisError("Failed to connect to Google Gemini API.")
        
        return self.client

    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Send resume text to Google Gemini API and obtain structured evaluation metrics.
        """
        client = self._get_client()

        prompt = f"""
You are an expert Senior HR Director, Executive Talent Recruiter, and Applicant Tracking System (ATS) Specialist with over 15 years of hiring experience.

Analyze the following resume text thoroughly and provide an in-depth evaluation in JSON format matching the schema provided.

Evaluation Directives:
1. Calculate a realistic, unbiased ATS Compatibility Score (0-100) based on structure, formatting readability, action verbs, quantifiable achievements, and keywords.
2. Provide a professional Executive Summary highlighting core experience and domain background.
3. Categorize Technical Skills and Soft Skills accurately.
4. Identify critical Missing Skills that modern recruiters look for in similar candidate profiles.
5. Identify top Strengths (with specific highlights) and Weaknesses (vague phrasing, missing metrics, formatting issues).
6. Provide concrete, actionable Improvement Suggestions to raise the resume score.
7. Point out specific Grammar, Phrasing, or Formatting Suggestions.
8. Recommend top 3-5 Best Suitable Job Roles for the candidate.
9. Classify Experience Level (Entry-Level, Junior, Mid-Level, Senior, Lead/Executive).
10. Detail a 3-5 step actionable Career Growth Roadmap for the next 1-3 years.
11. Provide 4-6 targeted Interview Preparation Tips based on the resume content.

RESUME CONTENT:
---
{resume_text}
---
"""

        # Models to try in order of preference (gemini-3.6-flash is primary active model)
        candidate_models = [
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-flash-latest",
            "gemini-2.0-flash"
        ]
        response = None
        last_exception = None

        for model_name in candidate_models:
            try:
                logger.info(f"Attempting resume analysis using model: '{model_name}'")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=ResumeAnalysisResponse,
                        temperature=0.3,
                    )
                )
                if response and response.text:
                    logger.info(f"Successfully received response from model: '{model_name}'")
                    break
            except Exception as model_err:
                logger.warning(f"Model '{model_name}' failed or unavailable: {str(model_err)}")
                last_exception = model_err

        if not response or not response.text:
            error_str = str(last_exception) if last_exception else "All candidate Gemini models failed."
            logger.error(f"Gemini API invocation failed across all candidate models: {error_str}")
            if "API_KEY" in error_str.upper() or "UNAUTHENTICATED" in error_str.upper():
                raise GeminiAnalysisError("Invalid Google Gemini API Key. Please check your GEMINI_API_KEY environment variable.")
            elif "QUOTA" in error_str.upper() or "RESOURCE_EXHAUSTED" in error_str.upper():
                raise GeminiAnalysisError("Gemini API quota exceeded or rate limit hit. Please try again shortly.")
            else:
                raise GeminiAnalysisError(f"Analysis Service Error: {error_str}")

        response_text = response.text

        try:
            # Parse JSON into dictionary
            data = json.loads(response_text)
            validated_response = ResumeAnalysisResponse(**data)
            return validated_response.model_dump()

        except json.JSONDecodeError as json_err:
            logger.error(f"JSON parsing error from Gemini response: {str(json_err)}")
            try:
                cleaned = re.sub(r"^```json\s*", "", response_text, flags=re.MULTILINE)
                cleaned = re.sub(r"^```\s*", "", cleaned, flags=re.MULTILINE).strip()
                data = json.loads(cleaned)
                return ResumeAnalysisResponse(**data).model_dump()
            except Exception:
                raise GeminiAnalysisError("Received malformed response format from engine.")
        except Exception as err:
            logger.error(f"Error parsing Gemini response data: {str(err)}")
            raise GeminiAnalysisError(f"Failed to parse analysis result: {str(err)}")
