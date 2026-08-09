The Interview Agent

An AI-powered technical interview system built for the 31-day Enterprise AI Engineering Cohort. It conducts a personalized, multi-turn technical interview based on a candidate's actual learning journey (completed missions, skipped days, attempts, signals), asks intelligent follow-up questions, and produces structured feedback at the end.

Built with Flask, Google Gemini, a RAG pipeline (Qdrant + curriculum retrieval), and a lightweight multi-agent architecture.

Table of Contents
 Architecture
 Project Structure
 Setup
 Running the App
 API Contract
 How the Interview Works
 Scoring & Evaluation
 Offline / No-API-Key Behavior
 Troubleshooting (Windows)

Architecture
Candidate Profile (candidate.json)
        │
        ▼
  Planner Agent  ──▶  RAG Retriever (Qdrant / local keyword fallback)
        │                     │
        ▼                     ▼
  8+ planned questions   Curriculum Context (curriculum.json)
        │
        ▼
  Question Agent  (turns a planned question into natural interviewer speech)
        │
        ▼
  Candidate answers  ──▶  Evaluation Agent  ──▶  Follow-up Agent (max 2 per question)
        │
        ▼
  Feedback Agent  (aggregates all evaluations into final structured feedback)

  Project Structure
ai-interview-agent/
├── app.py                     # Flask entrypoint, registers blueprints
├── api/
│   ├── interview.py           # POST /api/interview — the required endpoint
│   └── feedback.py            # GET /api/feedback/<session_id>
├── agents/
│   ├── planner_agent.py       # Builds the question plan (min 8 Qs, 4+ days)
│   ├── question_agent.py      # Rephrases a question into interviewer speech
│   ├── followup_agent.py      # Decides + generates follow-up questions
│   ├── evaluation_agent.py    # Scores each answer
│   └── feedback_agent.py      # Aggregates final feedback
├── graph/
│   └── state.py                # TypedDicts for the interview state schema
├── services/
│   ├── interview_manager.py   # Orchestrates the interview turn-by-turn
│   ├── session_manager.py     # In-memory session store
│   ├── candidate_analyzer.py  # Derives strengths/weaknesses from candidate.json
│   ├── curriculum_loader.py   # Loads and indexes curriculum.json
│   └── gemini_service.py      # Centralized Gemini client (+ mock fallback)
├── rag/
│   ├── qdrant_client.py       # Qdrant client (local or cloud), with fallback
│   ├── embeddings.py          # Gemini embeddings for curriculum chunks
│   ├── retriever.py           # Curriculum search (vector + local keyword fallback)
│   └── ingest.py              # One-time curriculum → Qdrant ingestion script
├── data/
│   ├── curriculum.json        # 31-day, 8-module cohort curriculum
│   ├── candidates.json        # Sample candidate profiles
│   └── technical-spec.md      # API contract this project implements
├── frontend/                  # Static UI served by Flask (index/interview/report)
└── requirements.txt

Setup
1. Create and activate a virtual environment
powershell
cd path\to\ai-interview-agent
python -m venv venv
.\venv\Scripts\Activate.ps1

If PowerShell blocks the activation script, run once:

powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
2. Install dependencies
powershell
pip install -r requirements.txt
3. Configure environment variables

Copy .env.example to .env and fill in a real Gemini API key from Google AI Studio:

GEMINI_API_KEY=your_real_key_here
AI_INTERVIEW_DEMO_MODE=0

Running the App
powershell
python app.py

API Contract

Implements the single endpoint defined in data/technical-spec.md.

Start an interview
POST /api/interview
{
  "sessionId": "abc-123",
  "candidate": { ...candidate.json }
}
json
{ "reply": "...", "done": false }
Continue the conversation
POST /api/interview
{
  "sessionId": "abc-123",
  "message": "candidate's answer"
}
json
{ "reply": "...", "done": false }
Completion

Once 8 questions have been answered (follow-ups replace, not extend, the count):

json
{
  "reply": "Interview completed.",
  "done": true,
  "feedback": {
    "summary": "...",
    "strengths": [],
    "gaps": [],
    "next": []
  }
}
