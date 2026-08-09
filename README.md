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
├── app.py                     
├── api/
│   ├── interview.py          
│   └── feedback.py            
├── agents/
│   ├── planner_agent.py      
│   ├── question_agent.py      
│   ├── followup_agent.py      
│   ├── evaluation_agent.py    
│   └── feedback_agent.py      
├── graph/
│   └── state.py                
├── services/
│   ├── interview_manager.py   
│   ├── session_manager.py   
│   ├── candidate_analyzer.py
│   ├── curriculum_loader.py   
│   └── gemini_service.py      
├── rag/
│   ├── qdrant_client.py       
│   ├── embeddings.py          
│   ├── retriever.py          
│   └── ingest.py              
├── data/
│   ├── curriculum.json        
│   ├── candidates.json      
│   └── technical-spec.md     
├── frontend/                 
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

Deploy on Vercel

1. Push this repository to GitHub.
2. Import the project in the Vercel dashboard (Framework Preset: Other).
3. Add environment variables in Vercel → Settings → Environment Variables:
   - `GEMINI_API_KEY` — required for live AI interviews
   - `AI_INTERVIEW_DEMO_MODE=0`
   - Optional: `QDRANT_URL` and `QDRANT_API_KEY` for cloud vector search
4. Deploy. No build command is required.

Static pages are served from `public/`. API routes are handled by the Flask app in `api/index.py`.

For local Vercel-style testing:

powershell
npx vercel dev

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
