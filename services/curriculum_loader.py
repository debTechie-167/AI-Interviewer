# services/curriculum_loader.py

"""
Curriculum Loader

Compatible with the actual curriculum.json structure:

{
    "cohort": "...",
    "modules": [...],
    "days": [...]
}

Used by:
- RAG Ingestion
- Planner Agent
- Question Agent
- Coverage Tracking
- Evaluation Agent
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import json


class CurriculumLoader:

    def __init__(self, curriculum_path: str):

        self.curriculum_path = Path(curriculum_path)

        self.curriculum_data = self._load_curriculum()

    # =====================================================
    # Internal Loader
    # =====================================================

    def _load_curriculum(self) -> Dict[str, Any]:

        if not self.curriculum_path.exists():

            raise FileNotFoundError(
                f"Curriculum file not found: {self.curriculum_path}"
            )

        with open(
            self.curriculum_path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    # =====================================================
    # Raw Data Access
    # =====================================================

    def get_curriculum(self) -> Dict[str, Any]:

        return self.curriculum_data

    def get_cohort_name(self) -> str:

        return self.curriculum_data.get(
            "cohort",
            ""
        )

    def get_modules(self) -> List[Dict]:

        return self.curriculum_data.get(
            "modules",
            []
        )

    def get_days(self) -> List[Dict]:

        return self.curriculum_data.get(
            "days",
            []
        )

    # =====================================================
    # Day Lookup
    # =====================================================

    def get_day(
        self,
        day_number: int
    ) -> Optional[Dict]:

        for day in self.get_days():

            if day.get("day") == day_number:

                return day

        return None

    def get_day_title(
        self,
        day_number: int
    ) -> str:

        day = self.get_day(day_number)

        if not day:
            return ""

        return day.get(
            "title",
            ""
        )

    def get_day_type(
        self,
        day_number: int
    ) -> str:

        day = self.get_day(day_number)

        if not day:
            return ""

        return day.get(
            "type",
            ""
        )

    # =====================================================
    # Curriculum Elements
    # =====================================================

    def get_tools(
        self,
        day_number: int
    ) -> List[str]:

        day = self.get_day(day_number)

        if not day:
            return []

        return day.get(
            "tools",
            []
        )

    def get_objectives(
        self,
        day_number: int
    ) -> List[str]:

        day = self.get_day(day_number)

        if not day:
            return []

        return day.get(
            "objectives",
            []
        )

    # =====================================================
    # Coverage Helpers
    # =====================================================

    def get_all_day_numbers(self) -> List[int]:

        return [
            day["day"]
            for day in self.get_days()
        ]

    def get_days_by_module(
        self,
        module_name: str
    ) -> List[Dict]:

        matching_days = []

        for day in self.get_days():

            if (
                day.get("module", "")
                .lower()
                == module_name.lower()
            ):
                matching_days.append(day)

        return matching_days

    # =====================================================
    # Interview Planning Helpers
    # =====================================================

    def get_completed_day_content(
        self,
        completed_days: List[int]
    ) -> List[Dict]:

        content = []

        for day in completed_days:

            day_data = self.get_day(day)

            if day_data:

                content.append(day_data)

        return content

    def get_skipped_day_content(
        self,
        skipped_days: List[int]
    ) -> List[Dict]:

        content = []

        for day in skipped_days:

            day_data = self.get_day(day)

            if day_data:

                content.append(day_data)

        return content

    # =====================================================
    # RAG Documents
    # =====================================================

    def build_rag_documents(
        self
    ) -> List[Dict]:

        """
        Converts curriculum days into
        vector-searchable documents.
        """

        documents = []

        for day in self.get_days():

            document = {

                "id": f"day_{day['day']}",

                "day": day["day"],

                "title": day.get(
                    "title",
                    ""
                ),

                "type": day.get(
                    "type",
                    ""
                ),

                "tools": day.get(
                    "tools",
                    []
                ),

                "objectives": day.get(
                    "objectives",
                    []
                ),

                "content": f"""
                Day {day['day']}

                Title:
                {day.get('title', '')}

                Type:
                {day.get('type', '')}

                Tools:
                {' , '.join(day.get('tools', []))}

                Objectives:
                {' | '.join(day.get('objectives', []))}
                """
            }

            documents.append(document)

        return documents

    # =====================================================
    # Statistics
    # =====================================================

    def total_days(self) -> int:

        return len(
            self.get_days()
        )

    def total_modules(self) -> int:

        return len(
            self.get_modules()
        )


# =====================================================
# Singleton Loader
# =====================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

CURRICULUM_FILE = (
    BASE_DIR
    / "data"
    / "curriculum.json"
)

curriculum_loader = CurriculumLoader(
    str(CURRICULUM_FILE)
)


# =====================================================
# Convenience Functions
# =====================================================

def get_day(day_number: int):

    return curriculum_loader.get_day(
        day_number
    )


def get_tools(day_number: int):

    return curriculum_loader.get_tools(
        day_number
    )


def get_objectives(day_number: int):

    return curriculum_loader.get_objectives(
        day_number
    )


def build_rag_documents():

    return curriculum_loader.build_rag_documents()


# =====================================================
# Debug
# =====================================================

if __name__ == "__main__":

    print(
        f"Cohort: "
        f"{curriculum_loader.get_cohort_name()}"
    )

    print(
        f"Days: "
        f"{curriculum_loader.total_days()}"
    )

    print(
        f"Modules: "
        f"{curriculum_loader.total_modules()}"
    )

    docs = curriculum_loader.build_rag_documents()

    print(
        f"RAG Documents: {len(docs)}"
    )
