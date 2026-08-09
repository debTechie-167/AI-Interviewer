# api/interview.py

import os
import pickle

from flask import (
    Blueprint,
    request,
    jsonify
)

from services.interview_manager import (
    interview_manager
)
from services.session_manager import (
    session_manager
)

interview_bp = Blueprint(
    "interview",
    __name__
)

TMP_DIR = "/tmp/sessions"
os.makedirs(TMP_DIR, exist_ok=True)


def _sync_session_from_disk(session_id: str):
    """Restore session using pickle to handle complex Python state objects."""
    if not session_manager.get_session(session_id):
        file_path = os.path.join(TMP_DIR, f"{session_id}.pkl")
        if os.path.exists(file_path):
            try:
                with open(file_path, "rb") as f:
                    state = pickle.load(f)
                    session_manager.sessions[session_id] = state
            except Exception:
                pass


def _persist_session_to_disk(session_id: str):
    """Persist active session state to /tmp storage."""
    state = session_manager.get_session(session_id)
    if state:
        file_path = os.path.join(TMP_DIR, f"{session_id}.pkl")
        try:
            with open(file_path, "wb") as f:
                pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception:
            pass


# =====================================================
# Hackathon Endpoint
# POST /api/interview
# =====================================================

@interview_bp.route(
    "/api/interview",
    methods=["POST"]
)
def interview():

    try:

        data = (
            request.get_json()
            or {}
        )

        session_id = data.get(
            "sessionId"
        )

        if not session_id:

            return jsonify(
                {
                    "reply":
                        "sessionId is required.",
                    "done":
                        True
                }
            ), 400

        # Sync state from disk in case of serverless container recycling
        _sync_session_from_disk(session_id)

        # ==========================================
        # Start Interview
        # ==========================================

        if "candidate" in data:

            candidate = data["candidate"]

            result = (
                interview_manager
                .start_interview(
                    session_id=
                        session_id,
                    candidate_profile=
                        candidate
                )
            )

            _persist_session_to_disk(session_id)

            return jsonify(
                result
            )

        # ==========================================
        # Conversation Turn
        # ==========================================

        if "message" in data:

            result = (
                interview_manager
                .submit_answer(
                    session_id=
                        session_id,
                    transcript=
                        data["message"]
                )
            )

            _persist_session_to_disk(session_id)

            return jsonify(
                result
            )

        return jsonify(
            {
                "reply":
                    (
                        "Invalid request."
                    ),
                "done":
                    True
            }
        ), 400

    except Exception as error:

        return jsonify(
            {
                "reply":
                    str(error),
                "done":
                    True
            }
        ), 500