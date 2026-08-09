# graph/state.py

"""
Central LangGraph State for the AI Interview Agent

Compatible with:
- curriculum.json (days/modules structure)
- candidate.json (member/missions/signals structure)
- Technical Specification
- Single POST /api/interview endpoint
"""

from typing import TypedDict, List, Dict, Optional, Any
from datetime import datetime


# =====================================================
# Candidate Models
# =====================================================

class Member(TypedDict):
    id: str
    name: str
    jobRole: str
    yearsExperience: int
    education: str
    status: str


class Mission(TypedDict, total=False):
    day: int
    title: str

    # Some missions may contain passed
    passed: bool

    # Some missions may contain skipped
    skipped: bool

    attempts: int


class Signals(TypedDict):
    commitDays: int
    missionsCompleted: int
    missionsFirstTry: int


class CandidateProfile(TypedDict):
    member: Member
    missions: List[Mission]
    signals: Signals


# =====================================================
# Question Models
# =====================================================

class Question(TypedDict):
    question_id: str

    question_text: str

    curriculum_day: int

    topic: str

    difficulty: str

    is_followup: bool

    parent_question_id: Optional[str]


# =====================================================
# Answer Models
# =====================================================

class Answer(TypedDict):
    question_id: str

    transcript: str

    audio_path: Optional[str]

    response_time_seconds: float


# =====================================================
# Conversation History
# =====================================================

class ConversationMessage(TypedDict):
    role: str          # ai | candidate
    message: str


# =====================================================
# Evaluation Models
# =====================================================

class Evaluation(TypedDict):
    question_id: str

    score: float

    technical_score: float

    communication_score: float

    reasoning_score: float

    strengths: List[str]

    weaknesses: List[str]

    feedback: str


    confidence_score: float


# =====================================================
# Curriculum Coverage
# =====================================================

class Coverage(TypedDict):
    curriculum_days_covered: List[int]

    topics_covered: List[str]

    tools_covered: List[str]

    objectives_covered: List[str]


# =====================================================
# Final Feedback
# Technical Specification Compatible
# =====================================================

class FinalFeedback(TypedDict):
    summary: str

    strengths: List[str]

    gaps: List[str]

    next: List[str]

    overall_score: float

    technical_score: float

    communication_score: float

    reasoning_score: float


# =====================================================
# Main Interview State
# =====================================================

class InterviewState(TypedDict):

    # -----------------------------------------
    # Session Information
    # -----------------------------------------

    session_id: str

    started_at: str

    ended_at: Optional[str]

    interview_status: str

    interview_completed: bool

    # -----------------------------------------
    # Candidate
    # -----------------------------------------

    candidate: CandidateProfile

    # -----------------------------------------
    # Interview Progress
    # -----------------------------------------

    max_questions: int

    current_question_number: int

    # -----------------------------------------
    # Questions
    # -----------------------------------------

    planned_questions: List[Question]

    asked_questions: List[Question]

    current_question: Optional[Question]

    # -----------------------------------------
    # Answers
    # -----------------------------------------

    answers: List[Answer]

    current_answer: Optional[Answer]

    # -----------------------------------------
    # Conversation Context
    # -----------------------------------------

    conversation_history: List[ConversationMessage]

    # -----------------------------------------
    # Retrieved RAG Context
    # -----------------------------------------

    retrieved_context: List[str]

    retrieved_topics: List[str]

    retrieved_learning_objectives: List[str]

    # -----------------------------------------
    # Evaluation
    # -----------------------------------------

    evaluations: List[Evaluation]

    # -----------------------------------------
    # Coverage Tracking
    # -----------------------------------------

    covered_days: List[int]

    coverage: Coverage

    # -----------------------------------------
    # Metrics
    # -----------------------------------------

    average_response_time: float

    total_speaking_time: float

    followup_questions_count: int

    # -----------------------------------------
    # Final Feedback
    # -----------------------------------------

    final_feedback: Optional[FinalFeedback]


# =====================================================
# Initial State Factory
# =====================================================

def create_initial_state(
    session_id: str,
    candidate_profile: CandidateProfile,
    max_questions: int = 8
) -> InterviewState:

    return {

        # Session

        "session_id": session_id,

        "started_at": datetime.utcnow().isoformat(),

        "ended_at": None,

        "interview_status": "initialized",

        "interview_completed": False,

        # Candidate

        "candidate": candidate_profile,

        # Interview Progress

        "max_questions": max_questions,

        "current_question_number": 0,

        # Questions

        "planned_questions": [],

        "asked_questions": [],

        "current_question": None,

        # Answers

        "answers": [],

        "current_answer": None,

        # Conversation

        "conversation_history": [],

        # RAG

        "retrieved_context": [],

        "retrieved_topics": [],

        "retrieved_learning_objectives": [],

        # Evaluation

        "evaluations": [],

        # Coverage

        "covered_days": [],

        "coverage": {
            "curriculum_days_covered": [],
            "topics_covered": [],
            "tools_covered": [],
            "objectives_covered": []
        },

        # Metrics

        "average_response_time": 0.0,

        "total_speaking_time": 0.0,

        "followup_questions_count": 0,

        # Final Feedback

        "final_feedback": None
    }


# =====================================================
# Utility Functions
# =====================================================

def add_conversation_message(
    state: InterviewState,
    role: str,
    message: str
) -> None:

    state["conversation_history"].append(
        {
            "role": role,
            "message": message
        }
    )


def mark_day_covered(
    state: InterviewState,
    day: int
) -> None:

    if day not in state["covered_days"]:

        state["covered_days"].append(day)

        state["coverage"][
            "curriculum_days_covered"
        ].append(day)
