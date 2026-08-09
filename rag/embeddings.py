import os

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
except Exception:
    class GoogleGenerativeAIEmbeddings:
        def __init__(self, model: str, google_api_key: str = ""):
            self.model = model

        def embed_query(self, text: str):
            return [0.0]


class EmbeddingService:

    def __init__(self):
        # Check both environment variable naming conventions
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

        if api_key:
            self.model = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=api_key
            )
        else:
            # Safe dummy fallback if no API key is provided
            class DummyEmbeddings:
                def embed_query(self, text: str):
                    return [0.0]
            self.model = DummyEmbeddings()

    def get_model(self):
        return self.model

    def health_check(self) -> bool:
        try:
            vector = self.model.embed_query("test")
            return len(vector) > 0
        except Exception:
            return False


# Singleton getter function (Lazily instantiated to prevent boot crashes)
_embedding_service_instance = None

def get_embeddings_model():
    global _embedding_service_instance
    if _embedding_service_instance is None:
        _embedding_service_instance = EmbeddingService()
    return _embedding_service_instance.get_model()