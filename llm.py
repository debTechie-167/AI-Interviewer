"""
llm.py
------
LLM integration layer for the AI Interviewer.

Design decisions:
- LLMClient is an abstract interface so the rest of the app never talks to
  Gemini directly. Swapping providers (Anthropic, a local model, etc.) later
  means writing one new class here -- interview.py and app.py stay untouched.
- If no API key is configured, we fall back to a deterministic mock client.
  This keeps the server runnable end-to-end (demo-able) even before you've
  wired up billing/keys during the hackathon.
"""

import os
import json
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()


class LLMClient(ABC):
    """Abstract interface every LLM provider must implement."""

    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Return a single text completion given a system + user prompt."""
        raise NotImplementedError


class GeminiClient(LLMClient):
    """
    Gemini-backed implementation. Requires GEMINI_API_KEY in the environment.
    Uses the current `google-genai` SDK (the older `google-generativeai`
    package is deprecated and no longer receiving updates).
    """

    def __init__(self, model: str = "gemini-2.0-flash"):
        from google import genai
        self._genai_types = __import__("google.genai.types", fromlist=["types"])
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_name = model

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config=self._genai_types.GenerateContentConfig(system_instruction=system_prompt),
        )
        return response.text.strip()


class MockClient(LLMClient):
    """
    Fallback client used when no API key is configured.
    Keeps the API contract intact (reply/done/feedback) without calling
    an external service, so the backend is demoable offline.
    """

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        if "FEEDBACK" in system_prompt:
            return json.dumps({
                "summary": "Candidate participated in a mock interview session (no LLM key configured).",
                "strengths": ["Engaged with each question"],
                "gaps": ["Connect a real LLM provider for meaningful evaluation"],
                "next": ["Set GEMINI_API_KEY to enable real question generation and scoring"]
            })
        return "Can you walk me through your approach to that in more detail?"


def get_llm_client() -> LLMClient:
    """Factory: picks Gemini if configured, else the mock fallback."""
    if os.getenv("GEMINI_API_KEY"):
        return GeminiClient(model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))
    return MockClient()


# --- Higher-level helpers used by interview.py -----------------------------

QUESTION_SYSTEM_PROMPT = """You are a professional technical interviewer conducting a live interview.
Ask ONE clear, concise, conversational question at a time.
Do not restate the candidate's previous answer at length.
Do not include numbering, labels, or meta-commentary -- output only the question text."""

EVAL_SYSTEM_PROMPT = """You are evaluating a candidate's interview answer.
Given the question and their answer, respond with a short internal note (1-2 sentences)
on correctness/depth. This is not shown to the candidate. Output plain text only."""

FEEDBACK_SYSTEM_PROMPT = """FEEDBACK GENERATION.
You are summarizing a completed technical interview.
Respond ONLY with valid JSON matching exactly this shape, no markdown fences, no extra text:
{"summary": "string", "strengths": ["string"], "gaps": ["string"], "next": ["string"]}"""


def generate_question(client: LLMClient, candidate: dict, topic: dict, history: list) -> str:
    history_text = "\n".join(f"{turn['role']}: {turn['content']}" for turn in history[-6:])
    user_prompt = f"""Candidate profile: {json.dumps(candidate)}
Current topic: {topic.get('name', 'General')} (difficulty: {topic.get('difficulty', 'medium')})
Seed questions for inspiration (don't quote verbatim, adapt to candidate): {topic.get('seed_questions', [])}

Recent conversation:
{history_text}

Ask the next interview question for this topic."""
    return client.complete(QUESTION_SYSTEM_PROMPT, user_prompt)


def evaluate_answer(client: LLMClient, question: str, answer: str) -> str:
    user_prompt = f"Question: {question}\nCandidate answer: {answer}"
    return client.complete(EVAL_SYSTEM_PROMPT, user_prompt)


def generate_feedback(client: LLMClient, candidate: dict, history: list) -> dict:
    transcript = "\n".join(f"{turn['role']}: {turn['content']}" for turn in history)
    user_prompt = f"""Candidate profile: {json.dumps(candidate)}

Full interview transcript:
{transcript}

Produce the final structured feedback JSON."""
    raw = client.complete(FEEDBACK_SYSTEM_PROMPT, user_prompt)
    try:
        # Strip accidental markdown fences if a model adds them anyway
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)
    except (json.JSONDecodeError, AttributeError):
        return {
            "summary": raw[:500] if raw else "Interview completed.",
            "strengths": [],
            "gaps": [],
            "next": []
        }