# services/session_manager.py

from typing import Dict, Optional

from graph.state import (
    InterviewState,
    CandidateProfile,
    create_initial_state,
    add_conversation_message,
    mark_day_covered
)


class SessionManager:

    def __init__(self):

        self.sessions: Dict[
            str,
            InterviewState
        ] = {}

    # =====================================================
    # Create Session
    # =====================================================

    def create_session(
        self,
        session_id: str,
        candidate_profile: CandidateProfile,
        max_questions: int = 8
    ) -> InterviewState:

        state = create_initial_state(
            session_id=session_id,
            candidate_profile=candidate_profile,
            max_questions=max_questions
        )

        self.sessions[session_id] = state

        return state

    # =====================================================
    # Get Session
    # =====================================================

    def get_session(
        self,
        session_id: str
    ) -> Optional[InterviewState]:

        return self.sessions.get(
            session_id
        )

    # =====================================================
    # Session Exists
    # =====================================================

    def exists(
        self,
        session_id: str
    ) -> bool:

        return session_id in self.sessions

    # =====================================================
    # Store Current Question
    # =====================================================

    def set_current_question(
        self,
        session_id: str,
        question: dict
    ) -> bool:

        state = self.get_session(
            session_id
        )

        if not state:
            return False

        state["current_question"] = question

        state["asked_questions"].append(
            question
        )

        state[
            "current_question_number"
        ] += 1

        add_conversation_message(
            state,
            "ai",
            question["question_text"]
        )

        day = question.get(
            "curriculum_day"
        )

        if day is not None:

            mark_day_covered(
                state,
                day
            )

        return True

    # =====================================================
    # Save Candidate Answer
    # =====================================================

    def save_answer(
        self,
        session_id: str,
        transcript: str,
        response_time: float = 0.0,
        audio_path: str | None = None
    ) -> bool:

        state = self.get_session(
            session_id
        )

        if not state:
            return False

        current_question = state.get(
            "current_question"
        )

        if not current_question:
            return False

        answer = {

            "question_id":
                current_question[
                    "question_id"
                ],

            "transcript":
                transcript,

            "audio_path":
                audio_path,

            "response_time_seconds":
                response_time
        }

        state["answers"].append(
            answer
        )

        state[
            "total_speaking_time"
        ] += response_time

        answer_count = len(
            state["answers"]
        )

        if answer_count > 0:

            state[
                "average_response_time"
            ] = round(

                state[
                    "total_speaking_time"
                ] / answer_count,

                2
            )

        add_conversation_message(
            state,
            "candidate",
            transcript
        )

        return True

    # =====================================================
    # Follow Up Counter
    # =====================================================

    def increment_followup_count(
        self,
        session_id: str
    ) -> None:

        state = self.get_session(
            session_id
        )

        if not state:
            return

        state[
            "followup_questions_count"
        ] += 1

    # =====================================================
    # Interview Complete
    # =====================================================

    def complete_interview(
        self,
        session_id: str,
        final_feedback: dict
    ) -> bool:

        state = self.get_session(
            session_id
        )

        if not state:
            return False

        state[
            "interview_completed"
        ] = True

        state[
            "interview_status"
        ] = "completed"

        state[
            "ended_at"
        ] = final_feedback.get(
            "completed_at"
        )

        state[
            "final_feedback"
        ] = final_feedback

        return True

    # =====================================================
    # Summary
    # =====================================================

    def get_summary(
        self,
        session_id: str
    ) -> Optional[dict]:

        state = self.get_session(
            session_id
        )

        if not state:
            return None

        return {

            "session_id":
                state["session_id"],

            "status":
                state[
                    "interview_status"
                ],

            "questions_asked":
                len(
                    state[
                        "asked_questions"
                    ]
                ),

            "answers_received":
                len(
                    state[
                        "answers"
                    ]
                ),

            "covered_days":
                state[
                    "covered_days"
                ],

            "followups":
                state[
                    "followup_questions_count"
                ],

            "average_response_time":
                state[
                    "average_response_time"
                ]
        }

    # =====================================================
    # Delete Session
    # =====================================================

    def delete_session(
        self,
        session_id: str
    ) -> bool:

        if session_id not in self.sessions:
            return False

        del self.sessions[
            session_id
        ]

        return True


# =====================================================
# Singleton Instance
# =====================================================

session_manager = SessionManager()
