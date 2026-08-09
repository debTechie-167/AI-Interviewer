# services/scoring_service.py

"""
Scoring Service

Hackathon Compatible Version

Purpose
-------
Aggregates Gemini/LLM evaluation results and generates:

- Overall Score
- Technical Score
- Communication Score
- Reasoning Score
- Confidence Score
- Verdict
- Summary
- Strengths
- Gaps
- Next Steps

Compatible with:
- state.py
- evaluation_agent.py
- feedback_agent.py
- report.html
- Technical Specification
"""

from typing import List, Dict, Any


class ScoringService:

    def __init__(self):

        self.weights = {

            "technical": 0.40,

            "reasoning": 0.30,

            "communication": 0.20,

            "confidence": 0.10
        }

    # =====================================================
    # Main Entry
    # =====================================================

    def build_final_report(
        self,
        evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        if not evaluations:

            return self._empty_report()

        technical_score = self._average(
            evaluations,
            "technical_score"
        )

        communication_score = self._average(
            evaluations,
            "communication_score"
        )

        reasoning_score = self._average(
            evaluations,
            "reasoning_score"
        )

        confidence_score = self._average(
            evaluations,
            "confidence_score"
        )

        overall_score = round(

            technical_score
            * self.weights["technical"]

            +

            reasoning_score
            * self.weights["reasoning"]

            +

            communication_score
            * self.weights["communication"]

            +

            confidence_score
            * self.weights["confidence"]

        )

        strengths = self._collect_unique(
            evaluations,
            "strengths"
        )

        gaps = self._collect_unique(
            evaluations,
            "weaknesses"
        )

        verdict = self._determine_verdict(
            overall_score
        )

        rating = self._determine_rating(
            overall_score
        )

        summary = self._generate_summary(
            overall_score,
            strengths,
            gaps
        )

        next_steps = self._generate_next_steps(
            gaps
        )

        return {

            # Main Scores

            "overall_score":
                overall_score,

            "technical_score":
                technical_score,

            "communication_score":
                communication_score,

            "reasoning_score":
                reasoning_score,

            "confidence_score":
                confidence_score,

            # Report

            "rating":
                rating,

            "verdict":
                verdict,

            "summary":
                summary,

            "strengths":
                strengths,

            "gaps":
                gaps,

            "next":
                next_steps,

            # Detailed Evaluations

            "question_evaluations":
                evaluations,

            "questions_evaluated":
                len(evaluations)
        }

    # =====================================================
    # Average Scores
    # =====================================================

    def _average(
        self,
        evaluations: List[Dict[str, Any]],
        field: str
    ) -> int:

        if not evaluations:
            return 0

        total = sum(

            evaluation.get(
                field,
                0
            )

            for evaluation in evaluations
        )

        return round(
            total / len(evaluations)
        )

    # =====================================================
    # Collect Unique Strengths/Gaps
    # =====================================================

    def _collect_unique(
        self,
        evaluations: List[Dict[str, Any]],
        field: str
    ) -> List[str]:

        values = []

        for evaluation in evaluations:

            items = evaluation.get(
                field,
                []
            )

            values.extend(items)

        unique = []

        for item in values:

            if item not in unique:

                unique.append(item)

        return unique

    # =====================================================
    # Verdict
    # =====================================================

    def _determine_verdict(
        self,
        score: int
    ) -> str:

        if score >= 90:
            return "Exceptional"

        if score >= 80:
            return "Strong Hire"

        if score >= 70:
            return "Hire"

        if score >= 60:
            return "Consider"

        return "No Hire"

    # =====================================================
    # Rating
    # =====================================================

    def _determine_rating(
        self,
        score: int
    ) -> str:

        if score >= 90:
            return "Exceptional"

        if score >= 80:
            return "Excellent"

        if score >= 70:
            return "Good"

        if score >= 60:
            return "Average"

        return "Needs Improvement"

    # =====================================================
    # Summary Generator
    # =====================================================

    def _generate_summary(
        self,
        overall_score: int,
        strengths: List[str],
        gaps: List[str]
    ) -> str:

        if overall_score >= 85:

            return (
                "The candidate demonstrated a strong "
                "understanding of cohort concepts and "
                "showed excellent technical reasoning "
                "throughout the interview."
            )

        if overall_score >= 70:

            return (
                "The candidate demonstrated a solid "
                "understanding of most concepts but "
                "has a few knowledge gaps that should "
                "be strengthened."
            )

        return (
            "The candidate requires additional "
            "practice and deeper understanding "
            "of core cohort concepts."
        )

    # =====================================================
    # Learning Recommendations
    # =====================================================

    def _generate_next_steps(
        self,
        gaps: List[str]
    ) -> List[str]:

        recommendations = []

        for gap in gaps:

            recommendations.append(
                f"Review and practice: {gap}"
            )

        if not recommendations:

            recommendations.append(
                "Continue solving advanced AI system design problems."
            )

        return recommendations

    # =====================================================
    # Technical Specification Feedback
    # =====================================================

    def build_hackathon_feedback(
        self,
        report: Dict[str, Any]
    ) -> Dict[str, Any]:

        return {

            "summary":
                report["summary"],

            "strengths":
                report["strengths"],

            "gaps":
                report["gaps"],

            "next":
                report["next"]
        }

    # =====================================================
    # Empty Report
    # =====================================================

    def _empty_report(self) -> Dict[str, Any]:

        return {

            "overall_score": 0,

            "technical_score": 0,

            "communication_score": 0,

            "reasoning_score": 0,

            "confidence_score": 0,

            "rating": "Not Evaluated",

            "verdict": "No Decision",

            "summary": "No interview data available.",

            "strengths": [],

            "gaps": [],

            "next": [],

            "question_evaluations": [],

            "questions_evaluated": 0
        }


# =====================================================
# Singleton
# =====================================================

scoring_service = ScoringService()


# =====================================================
# Example
# =====================================================

if __name__ == "__main__":

    evaluations = [

        {

            "question_id": "Q1",

            "technical_score": 88,

            "communication_score": 80,

            "reasoning_score": 90,

            "confidence_score": 84,

            "strengths": [
                "Strong RAG understanding"
            ],

            "weaknesses": [
                "Needs deeper MCP knowledge"
            ]
        },

        {

            "question_id": "Q2",

            "technical_score": 82,

            "communication_score": 78,

            "reasoning_score": 86,

            "confidence_score": 80,

            "strengths": [
                "Good agent architecture explanation"
            ],

            "weaknesses": [
                "Limited deployment experience"
            ]
        }
    ]

    report = scoring_service.build_final_report(
        evaluations
    )

    from pprint import pprint

    pprint(report)
