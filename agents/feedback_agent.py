
# agents/feedback_agent.py

"""
Feedback Agent

Responsibilities:
- Aggregate all interview evaluations
- Generate final interview summary
- Generate strengths
- Generate gaps
- Generate next learning actions
- Return FinalFeedback compatible with state.py
"""

from typing import List, Dict

from graph.state import (
    Evaluation,
    FinalFeedback,
    CandidateProfile
)

from services.gemini_service import (
    gemini_service
)


def run_feedback_agent(
    candidate: CandidateProfile,
    evaluations: List[Evaluation],
    covered_days: List[int]
) -> FinalFeedback:

    # ==========================================
    # Empty Interview Protection
    # ==========================================

    if not evaluations:

        return {

            "summary":
                "Interview could not be evaluated.",

            "strengths": [],

            "gaps": [
                "No interview data available."
            ],

            "next": [
                "Retake the interview."
            ],

            "overall_score": 0.0,

            "technical_score": 0.0,

            "communication_score": 0.0,

            "reasoning_score": 0.0
        }

    # ==========================================
    # Aggregate Scores
    # ==========================================

    total_score = sum(
        e["score"]
        for e in evaluations
    )

    technical_score = sum(
        e["technical_score"]
        for e in evaluations
    )

    communication_score = sum(
        e["communication_score"]
        for e in evaluations
    )

    reasoning_score = sum(
        e["reasoning_score"]
        for e in evaluations
    )

    count = len(evaluations)

    avg_score = round(
        total_score / count,
        2
    )

    avg_technical = round(
        technical_score / count,
        2
    )

    avg_communication = round(
        communication_score / count,
        2
    )

    avg_reasoning = round(
        reasoning_score / count,
        2
    )

    # ==========================================
    # Collect Strengths & Weaknesses
    # ==========================================

    strengths = []

    weaknesses = []

    for evaluation in evaluations:

        strengths.extend(
            evaluation.get(
                "strengths",
                []
            )
        )

        weaknesses.extend(
            evaluation.get(
                "weaknesses",
                []
            )
        )

    strengths = list(
        dict.fromkeys(strengths)
    )[:8]

    weaknesses = list(
        dict.fromkeys(weaknesses)
    )[:8]

    # ==========================================
    # Candidate Context
    # ==========================================

    member = candidate.get(
        "member",
        {}
    )

    candidate_name = member.get(
        "name",
        "Candidate"
    )

    role = member.get(
        "jobRole",
        "AI Engineer"
    )

    # ==========================================
    # AI Summary
    # ==========================================

    prompt = f"""
You are an expert AI interview evaluator.

Candidate:
{candidate_name}

Role:
{role}

Average Score:
{avg_score}/10

Technical Score:
{avg_technical}/10

Communication Score:
{avg_communication}/10

Reasoning Score:
{avg_reasoning}/10

Curriculum Days Covered:
{covered_days}

Strengths:
{strengths}

Weaknesses:
{weaknesses}

Return ONLY JSON:

{{
  "summary": "...",
  "strengths": [
    "...",
    "..."
  ],
  "gaps": [
    "...",
    "..."
  ],
  "next": [
    "...",
    "..."
  ]
}}
"""

    try:

        response = (
            gemini_service.generate_text(
                prompt=prompt,
                temperature=0.3
            )
        )

        import json

        start = response.find("{")
        end = response.rfind("}") + 1

        if start != -1 and end > start:
            data = json.loads(response[start:end])
        else:
            raise ValueError("Invalid JSON response format from model.")

        return {

            "summary":
                data.get(
                    "summary",
                    "Interview completed."
                ),

            "strengths":
                data.get(
                    "strengths",
                    strengths[:5]
                ),

            "gaps":
                data.get(
                    "gaps",
                    weaknesses[:5]
                ),

            "next":
                data.get(
                    "next",
                    [
                        "Continue practicing AI engineering concepts."
                    ]
                ),

            "overall_score":
                avg_score,

            "technical_score":
                avg_technical,

            "communication_score":
                avg_communication,

            "reasoning_score":
                avg_reasoning
        }

    except Exception:

        return {

            "summary":
                (
                    f"{candidate_name} demonstrated "
                    f"a reasonable understanding "
                    f"of AI engineering concepts."
                ),

            "strengths":
                strengths[:5],

            "gaps":
                weaknesses[:5],

            "next":
                [
                    "Review weak curriculum topics.",
                    "Practice explaining technical decisions.",
                    "Improve system design discussions."
                ],

            "overall_score":
                avg_score,

            "technical_score":
                avg_technical,

            "communication_score":
                avg_communication,

            "reasoning_score":
                avg_reasoning
        }
