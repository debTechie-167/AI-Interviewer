
# api/feedback.py

from flask import (
    Blueprint,
    jsonify
)

from services.session_manager import (
    session_manager
)

feedback_bp = Blueprint(
    "feedback",
    __name__
)


@feedback_bp.route(
    "/api/feedback/<session_id>",
    methods=["GET"]
)
def get_feedback(session_id):

    state = session_manager.get_session(
        session_id
    )

    if not state:

        return jsonify(
            {
                "success": False,
                "message": "Session not found"
            }
        ), 404

    feedback = state.get(
        "final_feedback"
    )

    if not feedback:

        return jsonify(
            {
                "success": False,
                "message":
                    "Interview not completed"
            }
        ), 400

    return jsonify(
        {
            "success": True,
            "feedback": feedback
        }
    )
