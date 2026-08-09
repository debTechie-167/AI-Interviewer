
# rag/ingest.py

"""
Curriculum Ingestion Pipeline

Flow:

curriculum.json
↓
Chunk Curriculum
↓
Gemini Embeddings
↓
Qdrant Storage

Run once before starting interviews.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, Any, List

from qdrant_client.models import (
    PointStruct
)

from rag.embeddings import (
    get_embeddings_model
)

from rag.qdrant_client import (
    qdrant_service
)


class CurriculumIngestor:

    def __init__(self):

        self.collection_name = (
            qdrant_service.collection_name
        )

        self.client = (
            qdrant_service.client
        )

        self.embeddings = (
            get_embeddings_model()
        )

    # =====================================================
    # Load Curriculum
    # =====================================================

    def load_curriculum(
        self,
        filepath: str
    ) -> Dict[str, Any]:

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    # =====================================================
    # Create Chunks
    # =====================================================

    def create_chunks(
        self,
        curriculum: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        chunks = []

        # -------------------------------------------------
        # Format 1
        # curriculum["modules"]
        # -------------------------------------------------

        if "modules" in curriculum:

            modules = curriculum.get(
                "modules",
                []
            )

            for module in modules:

                module_name = module.get(
                    "module",
                    "Unknown Module"
                )

                days = module.get(
                    "days",
                    []
                )

                for day in days:

                    chunks.append(
                        self._build_chunk(
                            module_name,
                            day
                        )
                    )

        # -------------------------------------------------
        # Format 2
        # curriculum["days"]
        # -------------------------------------------------

        elif "days" in curriculum:

            for day in curriculum["days"]:

                chunks.append(
                    self._build_chunk(
                        "General Curriculum",
                        day
                    )
                )

        return chunks

    # =====================================================
    # Build Single Chunk
    # =====================================================

    def _build_chunk(
        self,
        module_name: str,
        day_data: Dict[str, Any]
    ) -> Dict[str, Any]:

        day_number = day_data.get(
            "day",
            0
        )

        topic = (
            day_data.get("topic")
            or day_data.get("title")
            or "Unknown Topic"
        )

        objectives = (
            day_data.get(
                "learningObjectives",
                []
            )
            or day_data.get(
                "objectives",
                []
            )
        )

        tools = day_data.get(
            "tools",
            []
        )

        projects = day_data.get(
            "projects",
            []
        )

        exercises = day_data.get(
            "exercises",
            []
        )

        text = f"""
Module: {module_name}

Day: {day_number}

Topic:
{topic}

Objectives:
{' | '.join(objectives)}

Tools:
{' | '.join(tools)}

Projects:
{' | '.join(projects)}

Exercises:
{' | '.join(exercises)}
"""

        return {

            "id":
                str(
                    uuid.uuid4()
                ),

            "text":
                text,

            "day":
                day_number,

            "module":
                module_name,

            "topic":
                topic,

            "objectives":
                objectives,

            "tools":
                tools
        }

    # =====================================================
    # Ingest
    # =====================================================

    def ingest(
        self,
        curriculum_path: str
    ) -> None:

        curriculum = (
            self.load_curriculum(
                curriculum_path
            )
        )

        chunks = (
            self.create_chunks(
                curriculum
            )
        )

        try:

            if (
                hasattr(
                    qdrant_service,
                    "collection_exists"
                )
                and not qdrant_service.collection_exists()
            ):

                qdrant_service.create_collection()

        except Exception:

            qdrant_service.create_collection()

        points = []

        for chunk in chunks:

            vector = (
                self.embeddings.embed_query(
                    chunk["text"]
                )
            )

            points.append(

                PointStruct(

                    id=str(
                        chunk["id"]
                    ),

                    vector=vector,

                    payload={

                        "text":
                            chunk["text"],

                        "day":
                            chunk["day"],

                        "module":
                            chunk["module"],

                        "topic":
                            chunk["topic"],

                        "objectives":
                            chunk["objectives"],

                        "tools":
                            chunk["tools"]
                    }
                )
            )

        self.client.upsert(

            collection_name=
                self.collection_name,

            points=points
        )

        print(
            f"\n✅ Successfully ingested "
            f"{len(points)} curriculum chunks."
        )


# =====================================================
# Singleton
# =====================================================

curriculum_ingestor = (
    CurriculumIngestor()
)


# =====================================================
# Standalone Execution
# =====================================================

if __name__ == "__main__":

    curriculum_file = Path(
        "data/curriculum.json"
    )

    curriculum_ingestor.ingest(
        str(curriculum_file)
    )
