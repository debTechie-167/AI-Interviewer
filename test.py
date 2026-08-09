import json

from services.interview_manager import interview_manager

# ==========================================
# Load Candidate
# ==========================================

with open(
    "data/candidate.json",
    "r",
    encoding="utf-8"
) as f:

    candidate = json.load(f)

# ==========================================
# Start Interview
# ==========================================

session_id = "TEST_SESSION"

print("\nSTARTING INTERVIEW...\n")

response = interview_manager.start_interview(
    session_id=session_id,
    candidate_profile=candidate
)

print(
    "AI:",
    response["reply"]
)

# ==========================================
# Simulated Candidate Answers
# ==========================================

sample_answers = [

    "RAG combines retrieval and generation.",

    "Vector databases store embeddings.",

    "Prompt engineering improves outputs.",

    "LangGraph manages agent workflows.",

    "Qdrant is used for semantic search.",

    "Embeddings convert text into vectors.",

    "Chunking improves retrieval quality.",

    "Gemini can evaluate technical answers."
]

# ==========================================
# Run Entire Interview
# ==========================================

for answer in sample_answers:

    print(
        "\nCandidate:",
        answer
    )

    result = (
        interview_manager.submit_answer(
            session_id=session_id,
            transcript=answer
        )
    )

    print(
        "\nAI:",
        result["reply"]
    )

    if result["done"]:

        print(
            "\nINTERVIEW COMPLETE\n"
        )

        print(
            json.dumps(
                result["feedback"],
                indent=4
            )
        )

        break