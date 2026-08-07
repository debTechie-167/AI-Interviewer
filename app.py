"""
app.py
------
FastAPI entry point. Single endpoint: POST /api/interview.

Request shape varies by turn type (per spec):
  - Start:    {"sessionId": str, "candidate": {...}}
  - Turn:     {"sessionId": str, "message": str}
Response shape:
  - {"reply": str, "done": bool}                     (start / mid-interview)
  - {"reply": str, "done": true, "feedback": {...}}   (end)

Routing rule: if the incoming sessionId is new -> start; otherwise -> turn.
This matches the spec's "Interview Flow Logic" section exactly.
"""

from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from interview import SessionStore, InterviewManager

app = FastAPI(title="AI Interviewer")

store = SessionStore()
manager = InterviewManager(store)


class InterviewRequest(BaseModel):
    sessionId: str
    candidate: Optional[dict] = None
    message: Optional[str] = None


class Feedback(BaseModel):
    summary: str
    strengths: list[str]
    gaps: list[str]
    next: list[str]


class InterviewResponse(BaseModel):
    reply: str
    done: bool
    feedback: Optional[Feedback] = None


@app.post("/api/interview", response_model=InterviewResponse)
def interview(req: InterviewRequest):
    is_new_session = not store.exists(req.sessionId)

    if is_new_session:
        if req.candidate is None:
            raise HTTPException(
                status_code=400,
                detail="New session requires a 'candidate' object to start the interview."
            )
        result = manager.start(req.sessionId, req.candidate)
        return result

    if req.message is None:
        raise HTTPException(
            status_code=400,
            detail="Existing session requires a 'message' field for this turn."
        )

    result = manager.continue_turn(req.sessionId, req.message)
    return result


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)