# rag/embeddings.py

"""
Gemini Embeddings

Compatible with:

- Qdrant
- LangChain
- Gemini
- Vercel
- Flask
- AI Interview Agent
"""

import os

try:
    from langchain_google_genai import (
        GoogleGenerativeAIEmbeddings
    )
except Exception:
    # Minimal fallback for testing when langchain_google_genai is not installed.
    class GoogleGenerativeAIEmbeddings:
        def __init__(self, model: str, google_api_key: str):
            self.model = model

        def embed_query(self, text: str):
            return [0.0]



class EmbeddingService:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        # If no API key, use the fallback embedding class which does not require network.
        self.model = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key or ""
        )

    # ==========================================
    # Get Embedding Model
    # ==========================================

    def get_model(
        self
    ) -> GoogleGenerativeAIEmbeddings:

        return self.model

    # ==========================================
    # Health Check
    # ==========================================

    def health_check(
        self
    ) -> bool:

        try:

            vector = (
                self.model.embed_query(
                    "test"
                )
            )

            return len(vector) > 0

        except Exception:

            return False


# ==========================================
# Singleton
# ==========================================

embedding_service = (
    EmbeddingService()
)


def get_embeddings_model() -> GoogleGenerativeAIEmbeddings:
    return embedding_service.get_model()
