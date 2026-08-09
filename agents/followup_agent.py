# agents/followup_agent.py

"""
Follow-Up Agent

Responsibilities:
- Analyze candidate answer quality
- Decide whether a follow-up is needed
- Use curriculum context (RAG)
- Use conversation history
- Prevent excessive follow-ups
- Return Question object or None
"""

import json
import uuid

from typing import Optional, List

from graph.state import (
    Question,
    Answer,
    ConversationMessage
)

from services.gemini_service import (
    gemini_service
)


MAX_FOLLOWUPS = 2


def run_followup_agent(
    current_question: Question,
    current_answer: Answer,
    conversation_history: List[ConversationMessage],
    rag_context: List[str],
    followup_count: int
) -> Optional[Question]:

    # ==========================================
    # Follow-Up Limit
    # ==========================================

    if followup_count >= MAX_FOLLOWUPS:
        return None

    # ==========================================
    # Conversation Context
    # ==========================================

    history_text = ""

    recent_messages = conversation_history[-6:]

    for msg in recent_messages:

        history_text += (
            f"{msg['role']}: "
            f"{msg['message']}\n"
        )

    # ==========================================
    # RAG Context
    # ==========================================

    context_text = "\n".join(
        rag_context[:5]
    )

    # ==========================================
    # Prompt
    # ==========================================

    prompt = f"""
You are a senior AI technical interviewer.

Question:
{current_question['question_text']}

Topic:
{current_question['topic']}

Curriculum Day:
{current_question['curriculum_day']}

Candidate Answer:
{current_answer['transcript']}

Conversation History:
{history_text}

Relevant Curriculum Context:
{context_text}

Determine whether a follow-up question
is required.

Generate a follow-up ONLY if:

- The answer is incomplete
- Important concepts are missing
- The reasoning is weak
- The explanation is too shallow
- Clarification would improve evaluation

Do NOT generate a follow-up if:

- The answer is already strong
- The answer is complete
- The answer demonstrates understanding

Return ONLY valid JSON.

Format:

{{
  "needs_followup": true,
  "followup_question_text": "..."
}}

or

{{
  "needs_followup": false,
  "followup_question_text": ""
}}
"""

    try:

        response = (
            gemini_service.generate_text(
                prompt=prompt,
                temperature=0.2
            )
        )

        json_start = response.find("{")
        json_end = response.rfind("}") + 1

        if json_start == -1:
            return None

        data = json.loads(
            response[
                json_start:json_end
            ]
        )

        needs_followup = (
            data.get(
                "needs_followup",
                False
            )
        )

        followup_text = (
            data.get(
                "followup_question_text",
                ""
            )
        )

        if (
            needs_followup
            and followup_text.strip()
        ):

            return {

                "question_id":
                    f"FQ-{uuid.uuid4().hex[:8]}",

                "question_text":
                    followup_text,

                "curriculum_day":
                    current_question[
                        "curriculum_day"
                    ],

                "topic":
                    current_question[
                        "topic"
                    ],

                "difficulty":
                    current_question[
                        "difficulty"
                    ],

                "is_followup":
                    True,

                "parent_question_id":
                    current_question[
                        "question_id"
                    ]
            }

    except Exception as error:

        print(
            "Followup Agent Error:",
            error
        )

    return None
