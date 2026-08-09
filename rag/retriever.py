
# rag/retriever.py

"""
Curriculum Retriever

Flow:

Candidate Profile
↓
Weak Areas
↓
Qdrant Search
↓
Relevant Curriculum Context
↓
Gemini Question Generation

Compatible with:
- embeddings.py
- qdrant_client.py
- curriculum.json
- candidate_analyzer.py
- planner_agent.py
- question_agent.py
- evaluation_agent.py
- feedback_agent.py
"""

from typing import List, Dict, Any

from rag.embeddings import (
    get_embeddings_model
)

from rag.qdrant_client import (
    qdrant_service
)
from services.curriculum_loader import curriculum_loader


class CurriculumRetriever:

    def __init__(self):

        self.client = (
            qdrant_service.client
        )

        self.collection_name = (
            qdrant_service.collection_name
        )

        self.embeddings = (
            get_embeddings_model()
        )

    # =====================================================
    # Search Curriculum
    # =====================================================

    def search(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:

        try:
            query_vector = self.embeddings.embed_query(query)
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
        except Exception:
            results = []

        documents = []

        for result in results:

            payload = (
                result.payload or {}
            )

            documents.append({

                "score":
                    float(
                        result.score
                    ),

                "text":
                    payload.get(
                        "text",
                        ""
                    ),

                "day":
                    payload.get(
                        "day",
                        None
                    ),

                "module":
                    payload.get(
                        "module",
                        ""
                    ),

                "topic":
                    payload.get(
                        "topic",
                        ""
                    ),

                "objectives":
                    payload.get(
                        "objectives",
                        []
                    ),

                "tools":
                    payload.get(
                        "tools",
                        []
                    )
            })

        # A fresh local installation has no Qdrant collection yet. Use the
        # checked-in curriculum directly so the complete prototype remains
        # usable without a separate ingestion step or vector database.
        if documents:
            return documents

        query_words = set(query.lower().split())
        local_documents = []
        for day in curriculum_loader.get_days():
            searchable = " ".join([
                day.get("title", ""),
                day.get("module", ""),
                " ".join(day.get("tools", [])),
                " ".join(day.get("objectives", [])),
            ]).lower()
            score = len(query_words.intersection(searchable.split()))
            local_documents.append((score, day))

        local_documents.sort(key=lambda item: item[0], reverse=True)
        return [
            {
                "score": float(score),
                "text": "Day {0}: {1}. {2}".format(
                    day.get("day", ""),
                    day.get("title", ""),
                    " ".join(day.get("objectives", [])),
                ),
                "day": day.get("day"),
                "module": day.get("module", ""),
                "topic": day.get("title", ""),
                "objectives": day.get("objectives", []),
                "tools": day.get("tools", []),
            }
            for score, day in local_documents[:limit]
        ]

    # =====================================================
    # Retrieve Context
    # =====================================================

    def retrieve_context(
        self,
        query: str,
        limit: int = 5
    ) -> Dict[str, Any]:

        documents = self.search(
            query=query,
            limit=limit
        )

        context_text = []

        days = []
        topics = []
        objectives = []
        tools = []

        for doc in documents:

            if doc["text"]:
                context_text.append(
                    doc["text"]
                )

            day = doc.get("day")

            if (
                day is not None
                and day not in days
            ):
                days.append(day)

            topic = doc.get("topic")

            if (
                topic
                and topic not in topics
            ):
                topics.append(topic)

            for objective in doc.get(
                "objectives",
                []
            ):

                if (
                    objective
                    and objective not in objectives
                ):
                    objectives.append(
                        objective
                    )

            for tool in doc.get(
                "tools",
                []
            ):

                if (
                    tool
                    and tool not in tools
                ):
                    tools.append(
                        tool
                    )

        return {

            "context":
                "\n\n".join(
                    context_text
                ),

            "days":
                days,

            "topics":
                topics,

            "objectives":
                objectives,

            "tools":
                tools,

            "documents":
                documents
        }

    # =====================================================
    # Question Context
    # =====================================================

    def retrieve_for_question(
        self,
        topic: str
    ) -> List[str]:

        result = self.retrieve_context(
            query=topic,
            limit=5
        )

        return [
            item
            for item in result[
                "context"
            ].split("\n\n")
            if item.strip()
        ]

    # =====================================================
    # Evaluation Context
    # =====================================================

    def retrieve_for_evaluation(
        self,
        topic: str
    ) -> List[str]:

        result = self.retrieve_context(
            query=topic,
            limit=3
        )

        return [
            item
            for item in result[
                "context"
            ].split("\n\n")
            if item.strip()
        ]

    # =====================================================
    # Followup Context
    # =====================================================

    def retrieve_for_followup(
        self,
        topic: str
    ) -> List[str]:

        result = self.retrieve_context(
            query=topic,
            limit=2
        )

        return [
            item
            for item in result[
                "context"
            ].split("\n\n")
            if item.strip()
        ]

    # =====================================================
    # Candidate-Aware Retrieval
    # =====================================================

    def retrieve_for_candidate(
        self,
        candidate_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:

        weak_topics = (
            candidate_analysis.get(
                "weak_topics",
                []
            )
        )

        if not weak_topics:

            weak_topics = (
                candidate_analysis.get(
                    "gaps",
                    []
                )
            )

        if not weak_topics:

            weak_topics = [
                "RAG",
                "Vector Databases",
                "Prompt Engineering"
            ]

        combined_context = []

        covered_days = []
        covered_topics = []
        covered_objectives = []
        covered_tools = []

        for topic in weak_topics:

            result = self.retrieve_context(
                query=topic,
                limit=3
            )

            combined_context.append(
                result["context"]
            )

            for day in result["days"]:

                if day not in covered_days:
                    covered_days.append(
                        day
                    )

            for item in result["topics"]:

                if item not in covered_topics:
                    covered_topics.append(
                        item
                    )

            for item in result["objectives"]:

                if item not in covered_objectives:
                    covered_objectives.append(
                        item
                    )

            for item in result["tools"]:

                if item not in covered_tools:
                    covered_tools.append(
                        item
                    )

        return {

            "context":
                "\n\n".join(
                    combined_context
                ),

            "days":
                covered_days,

            "topics":
                covered_topics,

            "objectives":
                covered_objectives,

            "tools":
                covered_tools
        }

    # =====================================================
    # Ensure Minimum Curriculum Coverage
    # =====================================================

    def retrieve_interview_plan_context(
        self,
        candidate_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:

        result = (
            self.retrieve_for_candidate(
                candidate_analysis
            )
        )

        days = result["days"]

        if len(days) < 4:

            fallback = self.search(
                query="AI Engineering",
                limit=10
            )

            for doc in fallback:

                day = doc.get("day")

                if (
                    day is not None
                    and day not in days
                ):
                    days.append(day)

                if len(days) >= 4:
                    break

        result["days"] = days

        return result


# =====================================================
# Singleton
# =====================================================

curriculum_retriever = (
    CurriculumRetriever()
)


# =====================================================
# Testing
# =====================================================

if __name__ == "__main__":

    sample_query = (
        "Retrieval Augmented Generation"
    )

    result = (
        curriculum_retriever
        .retrieve_context(
            sample_query
        )
    )

    print(
        "\nRetrieved Days:",
        result["days"]
    )

    print(
        "\nRetrieved Topics:",
        result["topics"]
    )

    print(
        "\nContext Preview:\n"
    )

    print(
        result["context"][:1000]
    )
