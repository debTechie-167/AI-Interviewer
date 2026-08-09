
# api/interview.py

from flask import (
    Blueprint,
    request,
    jsonify
)

from services.interview_manager import (
    interview_manager
)

interview_bp = Blueprint(
    "interview",
    __name__
)

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
