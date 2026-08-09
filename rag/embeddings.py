import os

try:
    from google import genai
except Exception:
    genai = None


class _DummyEmbeddings:
    def embed_query(self, text: str):
        return [0.0]


class _GeminiEmbeddings:
    def __init__(self, api_key: str):
        self._client = genai.Client(api_key=api_key)

    def embed_query(self, text: str):
        response = self._client.models.embed_content(
            model="text-embedding-004",
            contents=text,
        )
        return response.embeddings[0].values


class EmbeddingService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

        if api_key and genai is not None:
            try:
                self.model = _GeminiEmbeddings(api_key)
                return
            except Exception:
                pass

        self.model = _DummyEmbeddings()

    def get_model(self):
        return self.model

    def health_check(self) -> bool:
        try:
            vector = self.model.embed_query("test")
            return len(vector) > 0
        except Exception:
            return False


_embedding_service_instance = None


def get_embeddings_model():
    global _embedding_service_instance
    if _embedding_service_instance is None:
        _embedding_service_instance = EmbeddingService()
    return _embedding_service_instance.get_model()
