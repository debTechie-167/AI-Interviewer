# services/gemini_service.py

"""
Gemini Service

Centralized Gemini client for:

- Question Generation
- Follow-up Generation
- Answer Evaluation
- Final Feedback Generation

Compatible with:
- state.py
- session_manager.py
- scoring_service.py
- curriculum_loader.py
- Hackathon Technical Specification
"""

import os
import json
from typing import Dict, Any, List

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


class GeminiService:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if (
            os.getenv("AI_INTERVIEW_DEMO_MODE") == "1"
            or not api_key
            or genai is None
        ):
            raise ValueError(
                "Gemini is not configured"
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "gemini-2.5-flash"

    # =====================================================
    # Generic Text Generation
    # =====================================================

    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7
    ) -> str:

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature
            )
        )

        return response.text

    # =====================================================
    # Generic JSON Generation
    # =====================================================

    def generate_json(
        self,
        prompt: str
    ) -> Dict[str, Any]:

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3
            )
        )

        try:
            return json.loads(
                response.text
            )

        except Exception:

            return {}

    # =====================================================
    # Generate Interview Questions
    # =====================================================

    def generate_questions(
        self,
        candidate_analysis: Dict[str, Any],
        curriculum_context: str,
        total_questions: int = 8
    ) -> List[Dict[str, Any]]:

        prompt = f"""
You are a senior AI interviewer.

Generate exactly {total_questions}
technical interview questions.

Requirements:

- Cover at least 4 curriculum days
- Focus on candidate weaknesses
- Questions must be conversational
- Return JSON ONLY

Curriculum Context:
{curriculum_context}

Candidate Analysis:
{json.dumps(candidate_analysis, indent=2)}

Return:

{{
  "questions": [
    {{
      "question_id": "Q1",
      "question_text": "...",
      "curriculum_day": 12,
      "topic": "RAG",
      "difficulty": "medium",
      "is_followup": false,
      "parent_question_id": null
    }}
  ]
}}
"""

        result = self.generate_json(
            prompt
        )

        return result.get(
            "questions",
            []
        )

    # =====================================================
    # Generate Follow-up Question
    # =====================================================

    def generate_followup(
        self,
        question: str,
        answer: str
    ) -> Dict[str, Any]:

        prompt = f"""
You are conducting a technical interview.

Original Question:
{question}

Candidate Answer:
{answer}

Generate ONE intelligent follow-up question.

Return JSON only:

{{
  "question_text": "...",
  "reason": "..."
}}
"""

        return self.generate_json(
            prompt
        )

    # =====================================================
    # Evaluate Answer
    # =====================================================

    def evaluate_answer(
        self,
        question: Dict[str, Any],
        answer: str,
        curriculum_context: str
    ) -> Dict[str, Any]:

        prompt = f"""
You are a senior technical interviewer.

Evaluate this answer.

Question:
{json.dumps(question, indent=2)}

Answer:
{answer}

Curriculum Context:
{curriculum_context}

Return JSON only:

{{
  "technical_score": 0,
  "communication_score": 0,
  "reasoning_score": 0,
  "confidence_score": 0,

  "strengths": [],

  "weaknesses": [],

  "feedback": "..."
}}

All scores must be 0-100.
"""

        result = self.generate_json(
            prompt
        )

        return {

            "question_id":
                question["question_id"],

            "score":
                round(

                    (
                        result.get(
                            "technical_score",
                            0
                        )
                        +
                        result.get(
                            "communication_score",
                            0
                        )
                        +
                        result.get(
                            "reasoning_score",
                            0
                        )
                        +
                        result.get(
                            "confidence_score",
                            0
                        )

                    ) / 4,

                    2
                ),

            "technical_score":
                result.get(
                    "technical_score",
                    0
                ),

            "communication_score":
                result.get(
                    "communication_score",
                    0
                ),

            "reasoning_score":
                result.get(
                    "reasoning_score",
                    0
                ),

            "confidence_score":
                result.get(
                    "confidence_score",
                    0
                ),

            "strengths":
                result.get(
                    "strengths",
                    []
                ),

            "weaknesses":
                result.get(
                    "weaknesses",
                    []
                ),

            "feedback":
                result.get(
                    "feedback",
                    ""
                )
        }

    # =====================================================
    # Generate Final Feedback
    # =====================================================

    def generate_final_feedback(
        self,
        report: Dict[str, Any]
    ) -> Dict[str, Any]:

        prompt = f"""
You are a senior technical interviewer.

Generate final interview feedback.

Interview Report:

{json.dumps(report, indent=2)}

Return JSON ONLY:

{{
  "summary": "...",

  "strengths": [],

  "gaps": [],

  "next": []
}}
"""

        result = self.generate_json(
            prompt
        )

        return {

            "summary":
                result.get(
                    "summary",
                    ""
                ),

            "strengths":
                result.get(
                    "strengths",
                    []
                ),

            "gaps":
                result.get(
                    "gaps",
                    []
                ),

            "next":
                result.get(
                    "next",
                    []
                ),

            "overall_score":
                report.get(
                    "overall_score",
                    0
                ),

            "technical_score":
                report.get(
                    "technical_score",
                    0
                ),

            "communication_score":
                report.get(
                    "communication_score",
                    0
                ),

            "reasoning_score":
                report.get(
                    "reasoning_score",
                    0
                )
        }


# =====================================================
# Singleton
# =====================================================


class _MockGeminiService:
    """A minimal mock used when GEMINI_API_KEY is not provided (test-friendly)."""

    def generate_text(self, prompt: str, temperature: float = 0.7) -> str:
        return "{}"

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        return {}

    def generate_questions(self, candidate_analysis: Dict[str, Any], curriculum_context: str, total_questions: int = 8) -> List[Dict[str, Any]]:
        return []

    def generate_followup(self, question: str, answer: str) -> Dict[str, Any]:
        return {}

    def evaluate_answer(self, question: Dict[str, Any], answer: str, curriculum_context: str) -> Dict[str, Any]:
        return {
            "question_id": question.get("question_id", ""),
            "score": 0,
            "technical_score": 0,
            "communication_score": 0,
            "reasoning_score": 0,
            "confidence_score": 0,
            "strengths": [],
            "weaknesses": [],
            "feedback": "",
        }

    def generate_final_feedback(self, report: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "summary": "",
            "strengths": [],
            "gaps": [],
            "next": [],
            "overall_score": report.get("overall_score", 0),
            "technical_score": report.get("technical_score", 0),
            "communication_score": report.get("communication_score", 0),
            "reasoning_score": report.get("reasoning_score", 0),
        }


try:
    gemini_service = GeminiService()
except Exception:
    gemini_service = _MockGeminiService()

