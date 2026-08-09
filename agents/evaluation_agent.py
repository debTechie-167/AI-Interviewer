# agents/evaluation_agent.py

import json

from graph.state import (
    Question,
    Answer,
    Evaluation
)

from services.gemini_service import (
    gemini_service
)


def run_evaluation_agent(
    question: Question,
    answer: Answer,
    rag_context: list[str],
    candidate: dict
) -> Evaluation:

    context_text = "\n".join(
        rag_context[:5]
    )

    prompt = f"""
You are an expert AI interview evaluator.

Question:
{question['question_text']}

Topic:
{question['topic']}

Curriculum Day:
{question['curriculum_day']}

Candidate Answer:
{answer['transcript']}

Relevant Curriculum Context:
{context_text}

Evaluate:

1. Technical Accuracy
2. Communication
3. Reasoning
4. Depth of Understanding

Return ONLY JSON.

{{
  "score": 0.0,
  "technical_score": 0.0,
  "communication_score": 0.0,
  "reasoning_score": 0.0,
  "strengths": [],
  "weaknesses": [],
  "feedback": ""
}}
"""

    try:

        response = (
            gemini_service.generate_text(
                prompt=prompt,
                temperature=0.2
            )
        )

        start = response.find("{")
        end = response.rfind("}") + 1

        if start != -1 and end > start:
            data = json.loads(response[start:end])
        else:
            raise ValueError("Invalid JSON response format from model.")

        return {

            "question_id":
                question["question_id"],

            "score":
                float(
                    data.get(
                        "score",
                        7.0
                    )
                ),

            "technical_score":
                float(
                    data.get(
                        "technical_score",
                        7.0
                    )
                ),

            "communication_score":
                float(
                    data.get(
                        "communication_score",
                        7.0
                    )
                ),

            "reasoning_score":
                float(
                    data.get(
                        "reasoning_score",
                        7.0
                    )
                ),

            "strengths":
                data.get(
                    "strengths",
                    []
                ),

            "weaknesses":
                data.get(
                    "weaknesses",
                    []
                ),

            "feedback":
                data.get(
                    "feedback",
                    ""
                )
        }

    except Exception:

        answer_length = len(
            answer["transcript"]
        )

        fallback_score = min(
            8.0,
            max(
                4.0,
                answer_length / 40
            )
        )

        return {

            "question_id":
                question["question_id"],

            "score":
                fallback_score,

            "technical_score":
                fallback_score,

            "communication_score":
                fallback_score,

            "reasoning_score":
                fallback_score,

            "strengths":
                [
                    "Attempted the question"
                ],

            "weaknesses":
                [
                    "Evaluation fallback used"
                ],

            "feedback":
                (
                    "Unable to perform "
                    "full AI evaluation."
                )
        }