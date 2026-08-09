# rag/qdrant_client.py

"""
Qdrant Client

Compatible with:

- Gemini Embeddings
- curriculum.json
- RAG Retrieval
- Flask
- Vercel
- AI Interview Agent
"""

import os

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance,
        VectorParams,
        PointStruct
    )
except Exception:
    # Minimal in-memory fallback for testing when qdrant_client is not installed.
    class Distance:
        COSINE = "cosine"

    class VectorParams:
        def __init__(self, size: int, distance: Distance):
            self.size = size
            self.distance = distance

    class PointStruct:
        def __init__(self, id: str, vector: list, payload: dict):
            self.id = id
            self.vector = vector
            self.payload = payload

    class _InMemoryCollection:
        def __init__(self, name: str):
            self.name = name

    class QdrantClient:
        def __init__(self, url: str = None, api_key: str = None, path: str = None):
            self._collections = {}

        def get_collections(self):
            class C: pass
            C.collections = [type('X', (), {'name': n}) for n in self._collections.keys()]
            return C

        def create_collection(self, collection_name: str, vectors_config: VectorParams):
            self._collections[collection_name] = {
                'vectors_config': vectors_config,
                'points': {}
            }

        def delete_collection(self, collection_name: str):
            if collection_name in self._collections:
                del self._collections[collection_name]

        def get_collection(self, collection_name: str):
            if collection_name in self._collections:
                return type('C', (), {'name': collection_name})
            raise Exception('collection not found')

        def upsert(self, collection_name: str, points: list):
            if collection_name not in self._collections:
                self.create_collection(collection_name, VectorParams(size=len(points[0].vector) if points else 0, distance=Distance.COSINE))
            for p in points:
                self._collections[collection_name]['points'][p.id] = p

        def search(self, collection_name: str, query_vector: list, limit: int = 5):
            # Return empty results for tests by default
            return []


class QdrantService:

    def __init__(self):

        self.collection_name = (
            "curriculum_knowledge"
        )

        qdrant_url = os.getenv(
            "QDRANT_URL"
        )

        qdrant_api_key = os.getenv(
            "QDRANT_API_KEY"
        )

        is_serverless = bool(
            os.getenv("VERCEL")
            or os.getenv("VERCEL_ENV")
            or os.getenv("AWS_LAMBDA_FUNCTION_NAME")
        )

        # -------------------------------
        # Cloud Mode
        # -------------------------------

        if qdrant_url:

            self.client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key
            )

        # -------------------------------
        # Serverless / Local Mode
        # -------------------------------

        elif is_serverless:

            # Vercel has a read-only filesystem except /tmp — avoid local disk.
            self.client = QdrantClient(":memory:")

        else:

            try:
                self.client = QdrantClient(
                    path="./qdrant_data"
                )
            except Exception:
                self.client = QdrantClient(":memory:")

    # =====================================
    # Create Collection
    # =====================================

    def create_collection(
        self,
        vector_size: int = 768
    ) -> None:

        collections = (
            self.client.get_collections()
        )

        existing = [

            c.name
            for c in collections.collections

        ]

        if self.collection_name in existing:
            return

        self.client.create_collection(

            collection_name=
                self.collection_name,

            vectors_config=
                VectorParams(

                    size=vector_size,

                    distance=
                        Distance.COSINE
                )
        )

    # =====================================
    # Delete Collection
    # =====================================

    def delete_collection(
        self
    ) -> None:

        self.client.delete_collection(
            self.collection_name
        )

    # =====================================
    # Get Collection Info
    # =====================================

    def get_collection_info(
        self
    ):

        return self.client.get_collection(
            self.collection_name
        )

    # =====================================
    # Health Check
    # =====================================

    def health_check(
        self
    ) -> bool:

        try:

            self.client.get_collections()

            return True

        except Exception:

            return False


# =====================================
# Singleton
# =====================================

qdrant_service = QdrantService()
