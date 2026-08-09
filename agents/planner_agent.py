# agents/planner_agent.py

"""
Planner Agent

Responsibilities:
- Analyze candidate profile
- Retrieve relevant curriculum context using RAG
- Generate interview plan
- Guarantee:
    - Minimum 8 questions
    - Minimum 4 curriculum days
- Return Question objects compatible with state.py
"""

from typing import List
import uuid

from graph.state import (
    CandidateProfile,
    Question
)

from services.candidate_analyzer import (
    CandidateAnalyzer
)

from services.gemini_service import (
    gemini_service
)

from rag.retriever import (
    curriculum_retriever
)
from services.curriculum_loader import curriculum_loader


def run_planner_agent(
    candidate: CandidateProfile,
    target_questions: int = 8
) -> List[Question]:

    # =====================================
    # Analyze Candidate
    # =====================================

    analyzer = CandidateAnalyzer(
        candidate
    )

    analysis = analyzer.analyze()

    # =====================================
    # Retrieve Curriculum Context
    # =====================================

    rag_context = (
        curriculum_retriever
        .retrieve_interview_plan_context(
            analysis
        )
    )

    curriculum_context = (
        rag_context["context"]
    )

    retrieved_days = (
        rag_context["days"]
    )

    # =====================================
    # Guarantee 4+ Days Coverage
    # =====================================

    if len(retrieved_days) < 4:

        fallback_days = [
            1, 7, 14, 21
        ]

        for day in fallback_days:

            if day not in retrieved_days:

                retrieved_days.append(
                    day
                )

            if len(retrieved_days) >= 4:
                break

    # =====================================
    # Gemini Question Generation
    # =====================================

    try:
        generated_questions = gemini_service.generate_questions(
            candidate_analysis=analysis,
            curriculum_context=curriculum_context,
            total_questions=target_questions
        )
    except Exception:
        # The local prototype remains demonstrable when an API key, network,
        # or hosted Gemini service is temporarily unavailable.
        generated_questions = []

    questions: List[
        Question
    ] = []

    # =====================================
    # Convert To State Schema
    # =====================================

    for index, item in enumerate(
        generated_questions
    ):

        questions.append(

            {

                "question_id":
                    item.get(
                        "question_id",
                        f"Q-{uuid.uuid4().hex[:8]}"
                    ),

                "question_text":
                    item.get(
                        "question_text",
                        "Explain the concept."
                    ),

                "curriculum_day":
                    item.get(
                        "curriculum_day",
                        retrieved_days[
                            index %
                            len(retrieved_days)
                        ]
                    ),

                "topic":
                    item.get(
                        "topic",
                        "General AI"
                    ),

                "difficulty":
                    item.get(
                        "difficulty",
                        "medium"
                    ),

                "is_followup":
                    False,

                "parent_question_id":
                    None
            }
        )

    # =====================================
    # Safety Fallback
    # =====================================

    while len(
        questions
    ) < target_questions:

        idx = len(
            questions
        )

        day_number = retrieved_days[
            idx % len(retrieved_days)
        ]
        day = curriculum_loader.get_day(day_number) or {}
        topic = day.get("title", "AI Engineering")
        objectives = day.get("objectives", [])
        objective = objectives[0] if objectives else topic
        prompts = [
            "Explain the core idea behind {topic} and when you would use it.",
            "How would you apply {topic} in a real production project?",
            "What trade-offs or failure modes should you consider when working with {topic}?",
            "Walk me through a practical approach to {objective}.",
            "How would you test that your implementation of {topic} is working correctly?",
            "Compare a simple and a production-ready approach to {topic}.",
            "Describe a common mistake with {topic} and how you would avoid it.",
            "If you had to explain {topic} to a teammate, what would you emphasize?",
        ]

        questions.append(

            {

                "question_id":
                    f"Q-{uuid.uuid4().hex[:8]}",

                "question_text":
                    prompts[idx % len(prompts)].format(
                        topic=topic,
                        objective=objective
                    ),

                "curriculum_day":
                    day_number,

                "topic":
                    topic,

                "difficulty":
                    "medium",

                "is_followup":
                    False,

                "parent_question_id":
                    None
            }
        )

    return questions[:target_questions]
