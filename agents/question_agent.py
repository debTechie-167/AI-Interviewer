# agents/question_agent.py

"""
Question Agent

Responsibilities:
- Convert planned question into natural spoken form
- Use RAG context
- Use conversation history
- Respect difficulty
- Handle follow-up questions
- Generate TTS-friendly interviewer speech
"""

from typing import List

from graph.state import (
    CandidateProfile,
    Question,
    ConversationMessage
)

from services.gemini_service import (
    gemini_service
)


def run_question_agent(
    candidate: CandidateProfile,
    raw_question: Question,
    rag_context: List[str],
    conversation_history: List[ConversationMessage]
) -> str:

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

    experience = member.get(
        "yearsExperience",
        0
    )

    # =====================================
    # Conversation Context
    # =====================================

    history_text = ""

    recent_history = (
        conversation_history[-6:]
    )

    for item in recent_history:

        history_text += (
            f"{item['role']}: "
            f"{item['message']}\n"
        )

    # =====================================
    # RAG Context
    # =====================================

    rag_text = "\n".join(
        rag_context[:5]
    )

    # =====================================
    # Follow-Up Handling
    # =====================================

    followup_note = ""

    if raw_question.get(
        "is_followup",
        False
    ):

        followup_note = """
This is a follow-up question.

Reference the candidate's
previous answer naturally.

Do NOT start a new topic.
"""

    # =====================================
    # Prompt
    # =====================================

    prompt = f"""
You are a senior AI interviewer.

Candidate:
Name: {candidate_name}
Role: {role}
Experience: {experience}

Curriculum Day:
{raw_question['curriculum_day']}

Topic:
{raw_question['topic']}

Difficulty:
{raw_question['difficulty']}

Question Objective:
{raw_question['question_text']}

Conversation History:
{history_text}

Retrieved Curriculum Context:
{rag_text}

{followup_note}

Your task:

Convert the question into a natural,
spoken interviewer question.

Requirements:

- Sound like a real interviewer.
- Maximum 3 sentences.
- Suitable for text-to-speech.
- Technical and professional.
- Do not greet the candidate.
- Do not introduce yourself.
- Do not say "here is the question".
- If follow-up, connect naturally to
  the previous discussion.
- Respect the difficulty level.
- Focus on understanding, reasoning,
  and engineering decisions.

Return ONLY the spoken question.
"""

    try:
        response = gemini_service.generate_text(
            prompt=prompt,
            temperature=0.7
        )
    except Exception:
        response = raw_question["question_text"]

    spoken_question = response.strip()
    if not spoken_question or spoken_question == "{}":
        return raw_question["question_text"]
    return spoken_question
