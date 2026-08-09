
# services/interview_manager.py

from typing import Dict, Any

from services.session_manager import (
    session_manager
)

from agents.planner_agent import (
    run_planner_agent
)

from agents.question_agent import (
    run_question_agent
)

from agents.followup_agent import (
    run_followup_agent
)

from agents.evaluation_agent import (
    run_evaluation_agent
)

from agents.feedback_agent import (
    run_feedback_agent
)


class InterviewManager:

    @staticmethod
    def _question_payload(state: Dict[str, Any], question: Dict[str, Any], spoken_question: str) -> Dict[str, Any]:
        """Translate agent state into the payload consumed by interview.html."""
        day = question.get("curriculum_day")
        if day is not None and day not in state["covered_days"]:
            state["covered_days"].append(day)
            state["coverage"]["curriculum_days_covered"].append(day)
        state["asked_questions"].append(question)

        return {
            "reply": spoken_question,
            "text": spoken_question,
            "topic": question.get("topic", "AI Engineering"),
            "difficulty": question.get("difficulty", "medium"),
            "is_followup": question.get("is_followup", False),
            "totalQuestions": state["max_questions"],
            "covered_days": state["covered_days"],
            "done": False,
        }

    # =====================================
    # Start Interview
    # =====================================

    def start_interview(
        self,
        session_id: str,
        candidate_profile: Dict[str, Any]
    ) -> Dict[str, Any]:

        state = session_manager.create_session(
            session_id=session_id,
            candidate_profile=candidate_profile,
            max_questions=8
        )

        planned_questions = (
            run_planner_agent(
                candidate_profile,
                target_questions=8
            )
        )

        state["planned_questions"] = (
            planned_questions
        )

        first_question = (
            planned_questions[0]
        )

        state["current_question"] = (
            first_question
        )

        state[
            "current_question_number"
        ] = 1

        spoken_question = (
            run_question_agent(
                candidate=candidate_profile,
                raw_question=first_question,
                rag_context=[],
                conversation_history=[]
            )
        )

        state["conversation_history"].append(
            {
                "role": "ai",
                "message": spoken_question
            }
        )

        state["interview_status"] = (
            "in_progress"
        )

        return self._question_payload(state, first_question, spoken_question)

    # =====================================
    # Submit Answer
    # =====================================

    def submit_answer(
        self,
        session_id: str,
        transcript: str
    ) -> Dict[str, Any]:

        state = (
            session_manager.get_session(
                session_id
            )
        )

        if not state:

            return {

                "reply":
                    "Session not found.",

                "done":
                    True
            }

        current_question = (
            state["current_question"]
        )

        answer = {

            "question_id":
                current_question[
                    "question_id"
                ],

            "transcript":
                transcript,

            "audio_path":
                None,

            "response_time_seconds":
                0.0
        }

        state["answers"].append(
            answer
        )

        state[
            "conversation_history"
        ].append(

            {
                "role":
                    "candidate",

                "message":
                    transcript
            }
        )

        evaluation = (
            run_evaluation_agent(
                question=current_question,
                answer=answer,
                rag_context=
                    state.get(
                        "retrieved_context",
                        []
                    ),
                candidate=
                    state["candidate"]
            )
        )

        state["evaluations"].append(
            evaluation
        )

        # The interview always ends after exactly `max_questions` candidate
        # answers. Follow-ups are adaptive replacements, not extra questions
        # beyond the advertised eight-question session.
        if len(state["answers"]) >= state["max_questions"]:
            return self.complete_interview(session_id)

        followup = (
            run_followup_agent(
                current_question=
                    current_question,

                current_answer=
                    answer,

                conversation_history=
                    state[
                        "conversation_history"
                    ],

                rag_context=
                    state.get(
                        "retrieved_context",
                        []
                    ),

                followup_count=
                    state.get(
                        "followup_questions_count",
                        0
                    )
            )
        )

        if followup:

            state[
                "followup_questions_count"
            ] += 1

            state[
                "current_question"
            ] = followup

            spoken_question = (
                run_question_agent(
                    candidate=
                        state["candidate"],

                    raw_question=
                        followup,

                    rag_context=
                        state.get(
                            "retrieved_context",
                            []
                        ),

                    conversation_history=
                        state[
                            "conversation_history"
                        ]
                )
            )

            state[
                "conversation_history"
            ].append(

                {
                    "role":
                        "ai",

                    "message":
                        spoken_question
                }
            )

            return self._question_payload(state, followup, spoken_question)

        next_index = (
            state[
                "current_question_number"
            ]
        )

        if next_index >= len(
            state["planned_questions"]
        ):

            return self.complete_interview(
                session_id
            )

        next_question = (
            state[
                "planned_questions"
            ][next_index]
        )

        state[
            "current_question"
        ] = next_question

        state[
            "current_question_number"
        ] += 1

        spoken_question = (
            run_question_agent(
                candidate=
                    state["candidate"],

                raw_question=
                    next_question,

                rag_context=
                    state.get(
                        "retrieved_context",
                        []
                    ),

                conversation_history=
                    state[
                        "conversation_history"
                    ]
            )
        )

        state[
            "conversation_history"
        ].append(

            {
                "role":
                    "ai",

                "message":
                    spoken_question
            }
        )

        return self._question_payload(state, next_question, spoken_question)

    # =====================================
    # Complete Interview
    # =====================================

    def complete_interview(
        self,
        session_id: str
    ) -> Dict[str, Any]:

        state = (
            session_manager.get_session(
                session_id
            )
        )

        feedback = (
            run_feedback_agent(
                candidate=
                    state["candidate"],

                evaluations=
                    state[
                        "evaluations"
                    ],

                covered_days=
                    state.get(
                        "covered_days",
                        []
                    )
            )
        )

        state[
            "final_feedback"
        ] = feedback

        state[
            "interview_completed"
        ] = True

        state[
            "interview_status"
        ] = "completed"

        member = state["candidate"].get("member", {})
        evaluations = state["evaluations"]
        question_by_id = {item["question_id"]: item for item in state["asked_questions"]}
        answer_by_id = {item["question_id"]: item for item in state["answers"]}
        score = round(feedback["overall_score"] * 10)
        strengths = feedback.get("strengths", []) or ["Completed the interview"]
        gaps = feedback.get("gaps", []) or ["Continue practising technical explanations"]
        topics = [question_by_id.get(item["question_id"], {}).get("topic", "AI Engineering") for item in evaluations]
        report = {
            "candidateName": member.get("name", "Candidate"),
            "overallScore": score,
            "technicalScore": round(feedback["technical_score"] * 10),
            "communicationScore": round(feedback["communication_score"] * 10),
            "performanceRating": "Strong" if score >= 80 else "Developing" if score >= 60 else "Needs practice",
            "radar": {"labels": topics or ["AI Engineering"], "scores": [round(item["score"] * 10) for item in evaluations] or [0]},
            "metrics": [
                {"name": "Technical Knowledge", "score": round(feedback["technical_score"] * 10), "trend": [round(item["technical_score"] * 10) for item in evaluations] or [0]},
                {"name": "Communication", "score": round(feedback["communication_score"] * 10), "trend": [round(item["communication_score"] * 10) for item in evaluations] or [0]},
                {"name": "Reasoning Ability", "score": round(feedback["reasoning_score"] * 10), "trend": [round(item["reasoning_score"] * 10) for item in evaluations] or [0]},
            ],
            "strengths": [{"title": item, "detail": item} for item in strengths],
            "weaknesses": [{"title": item, "detail": item} for item in gaps],
            "questions": [
                {"topic": question_by_id.get(item["question_id"], {}).get("topic", "AI Engineering"), "question": question_by_id.get(item["question_id"], {}).get("question_text", "Question"), "answerSummary": answer_by_id.get(item["question_id"], {}).get("transcript", ""), "notes": item.get("feedback", ""), "score": round(item["score"])}
                for item in evaluations
            ],
            "feedback": {"summary": feedback["summary"], "technical": "Technical score: " + str(round(feedback["technical_score"] * 10)) + "/100.", "communication": "Communication score: " + str(round(feedback["communication_score"] * 10)) + "/100.", "verdict": "Interview complete"},
            "roadmap": {"recommended": feedback.get("next", []), "studyAreas": gaps, "nextGoals": feedback.get("next", [])},
            "coverage": [{"name": "Day " + str(day), "pct": 100} for day in state["covered_days"]],
        }

        return {

            "reply":
                "Interview completed.",

            "done":
                True,

            "feedback": report,
            "covered_days": state["covered_days"],
            "coverage": report["coverage"]
        }


interview_manager = (
    InterviewManager()
)
