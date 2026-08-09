# AI Usage Log & Prompts History

This project was vibe-coded using AI assistance (Gemini / Claude / ChatGPT) for architectural planning, bug fixing, and serverless optimization.

## Key Prompts Used During Development

### 1. Architecture & Vercel Deployment
- "Configure `vercel.json` and Flask backend for serverless deployment on Vercel."
- "Fix Vercel serverless stateless session wipes by adding `/tmp` disk persistence using `pickle`."
- "Ensure static frontend pages (`index.html`, routing) work alongside Flask `/api` endpoints without 404 errors."

### 2. AI Agents & RAG Retrieval
- "Implement evaluation and feedback agents using Gemini API with robust JSON parsing fallbacks."
- "Add a safe fallback for `CurriculumRetriever` so the app defaults to local JSON when vector databases fail."

### 3. Debugging & Code Audits
- "Audit Flask API endpoints and resolve route precedence bugs for `/api/candidates` and static file serving."
- "Fix `TypeError` edge cases when Gemini returns empty or null response fields."