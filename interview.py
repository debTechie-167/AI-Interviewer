"""
interview.py
------------
Session state and interview progression logic.

Design decisions:
- SessionStore wraps a plain in-memory dict behind a small class. If you later
  need persistence across server restarts (multiple hackathon judges, etc.),
  swap this one class for a SQLite/SQLAlchemy-backed version -- app.py and
  the rest of interview.py don't need to change.
- Topic advancement is driven by curriculum.json's min_questions/max_questions
  per topic. If curriculum.json is empty or malformed (e.g. not filled in yet),
  we fall back to a single generic topic so the server never crashes on a
  bad/blank data file -- it just asks generic questions until max_total_turns.
- End-of-interview = current topic's max_questions reached AND it was the
  last topic, OR max_total_turns reached (whichever comes first). This
  guards against an interview running forever if candidates give very long
  answers.
"""

import json
import os

from llm import get_llm_client, generate_question, evaluate_answer, generate_feedback
from datetime import datetime, timezone

CURRICULUM_PATH = os.path.join(os.path.dirname(__file__), "data", "curriculum.json")

DEFAULT_TOPIC = {
    "id": "general",
    "name": "General Technical Discussion",
    "difficulty": "medium",
    "min_questions": 3,
    "max_questions": 6,
    "seed_questions": ["Tell me about a technical project you're proud of."]
}
DEFAULT_MAX_TOTAL_TURNS = 12


class SessionStore:
    """In-memory session storage keyed by sessionId."""

    def __init__(self):
        self._sessions = {}

    def exists(self, session_id):
        return session_id in self._sessions

    def get(self, session_id):
        return self._sessions.get(session_id)

    def save(self, session_id, state):
        self._sessions[session_id] = state


def _load_curriculum():
    """Load curriculum.json, falling back to sane defaults if missing/blank."""
    try:
        with open(CURRICULUM_PATH, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    topics = data.get("topics") or [DEFAULT_TOPIC]
    max_total_turns = data.get("max_total_turns") or DEFAULT_MAX_TOTAL_TURNS
    return {"topics": topics, "max_total_turns": max_total_turns}


class InterviewManager:
    """Owns the full lifecycle of an interview session."""

    def __init__(self, store: SessionStore):
        self.store = store
        self.llm = get_llm_client()

    def start(self, session_id: str, candidate: dict) -> dict:
        curriculum = _load_curriculum()
        topics = curriculum["topics"]

        state = {
            "candidate": candidate,
            "topics": topics,
            "max_total_turns": curriculum["max_total_turns"],
            "topic_index": 0,
            "questions_asked_in_topic": 0,
            "total_turns": 0,
            "history": [],  # list of {"role": "interviewer"|"candidate", "content": str}
            "done": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        first_topic = topics[0]
        question = generate_question(self.llm, candidate, first_topic, state["history"])

        state["history"].append({"role": "interviewer", "content": question})
        state["questions_asked_in_topic"] = 1
        state["total_turns"] = 1
        self.store.save(session_id, state)

        return {"reply": question, "done": False}

    def continue_turn(self, session_id: str, message: str) -> dict:
        state = self.store.get(session_id)
        if state is None:
            return {
                "reply": "No active interview found for this sessionId. Start a new interview first.",
                "done": True,
                "feedback": {"summary": "Invalid session.", "strengths": [], "gaps": [], "next": []}
            }

        if state["done"]:
            return {"reply": "Interview completed.", "done": True, "feedback": state.get("feedback", {})}

        state["history"].append({"role": "candidate", "content": message})

        last_question = next(
            (t["content"] for t in reversed(state["history"]) if t["role"] == "interviewer"),
            ""
        )
        # Evaluation note is generated for future scoring/telemetry use;
        # not surfaced to the candidate directly.
        _ = evaluate_answer(self.llm, last_question, message)

        state["total_turns"] += 1

        should_end = self._advance_or_end(state)

        if should_end:
            feedback = generate_feedback(self.llm, state["candidate"], state["history"])
            state["done"] = True
            state["feedback"] = feedback
            self.store.save(session_id, state)
            return {"reply": "Interview completed.", "done": True, "feedback": feedback}

        current_topic = state["topics"][state["topic_index"]]
        question = generate_question(self.llm, state["candidate"], current_topic, state["history"])
        state["history"].append({"role": "interviewer", "content": question})
        self.store.save(session_id, state)

        return {"reply": question, "done": False}

    def _advance_or_end(self, state: dict) -> bool:
        """
        Mutates state['topic_index'] / ['questions_asked_in_topic'] to move
        through the curriculum. Returns True if the interview should end.
        """
        if state["total_turns"] >= state["max_total_turns"]:
            return True

        topics = state["topics"]
        max_q = topics[state["topic_index"]].get("max_questions", 1)

        state["questions_asked_in_topic"] += 1

        if state["questions_asked_in_topic"] > max_q:
            state["topic_index"] += 1
            state["questions_asked_in_topic"] = 0
            if state["topic_index"] >= len(topics):
                return True

        return False