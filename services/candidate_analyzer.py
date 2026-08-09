# services/candidate_analyzer.py

"""
Candidate Analyzer

Purpose:
---------
Analyzes candidate.json and extracts:

- Completed curriculum days
- Failed curriculum days
- Skipped curriculum days
- Strong topics
- Weak topics
- Completion ratio
- First-try success ratio
- Interview difficulty

Used by:
---------
planner_agent.py
question_agent.py
followup_agent.py
interview_manager.py
"""

from typing import Dict, List, Any


class CandidateAnalyzer:

    def __init__(self, candidate_data: Dict[str, Any]):

        self.candidate = candidate_data

        self.member = candidate_data.get(
            "member",
            {}
        )

        self.missions = candidate_data.get(
            "missions",
            []
        )

        self.signals = candidate_data.get(
            "signals",
            {}
        )

    # =====================================================
    # Mission Analysis
    # =====================================================

    def get_completed_days(self) -> List[int]:

        completed = []

        for mission in self.missions:

            if mission.get("passed") is True:

                completed.append(
                    mission["day"]
                )

        return sorted(completed)

    def get_skipped_days(self) -> List[int]:

        skipped = []

        for mission in self.missions:

            if mission.get("skipped") is True:

                skipped.append(
                    mission["day"]
                )

        return sorted(skipped)

    def get_failed_days(self) -> List[int]:

        failed = []

        for mission in self.missions:

            if (
                mission.get("passed") is False
                and mission.get("skipped") is not True
            ):
                failed.append(
                    mission["day"]
                )

        return sorted(failed)

    # =====================================================
    # Topic Strength Analysis
    # =====================================================

    def get_strong_days(self) -> List[int]:

        strong = []

        for mission in self.missions:

            attempts = mission.get(
                "attempts",
                999
            )

            passed = mission.get(
                "passed",
                False
            )

            if passed and attempts == 1:

                strong.append(
                    mission["day"]
                )

        return sorted(strong)

    def get_weak_days(self) -> List[int]:

        weak = []

        for mission in self.missions:

            attempts = mission.get(
                "attempts",
                0
            )

            passed = mission.get(
                "passed",
                False
            )

            skipped = mission.get(
                "skipped",
                False
            )

            if skipped:

                weak.append(
                    mission["day"]
                )

            elif passed and attempts >= 3:

                weak.append(
                    mission["day"]
                )

            elif not passed:

                weak.append(
                    mission["day"]
                )

        return sorted(
            list(set(weak))
        )

    # =====================================================
    # Metrics
    # =====================================================

    def completion_ratio(self) -> float:

        total = len(self.missions)

        if total == 0:
            return 0.0

        completed = len(
            self.get_completed_days()
        )

        return round(
            completed / total,
            2
        )

    def first_try_ratio(self) -> float:

        completed = self.get_completed_days()

        if len(completed) == 0:
            return 0.0

        first_try = len(
            self.get_strong_days()
        )

        return round(
            first_try / len(completed),
            2
        )

    # =====================================================
    # Interview Difficulty
    # =====================================================

    def determine_difficulty(self) -> str:

        completion = self.completion_ratio()

        first_try = self.first_try_ratio()

        commit_days = self.signals.get(
            "commitDays",
            0
        )

        if (
            completion >= 0.90
            and first_try >= 0.70
            and commit_days >= 20
        ):
            return "hard"

        elif (
            completion >= 0.70
        ):
            return "medium"

        return "easy"

    # =====================================================
    # Coverage Recommendation
    # =====================================================

    def recommended_question_count(self) -> int:

        difficulty = self.determine_difficulty()

        if difficulty == "hard":
            return 10

        if difficulty == "medium":
            return 8

        return 8

    # =====================================================
    # Summary
    # =====================================================

    def analyze(self) -> Dict[str, Any]:

        return {

            "candidate_id":
                self.member.get(
                    "id"
                ),

            "candidate_name":
                self.member.get(
                    "name"
                ),

            "job_role":
                self.member.get(
                    "jobRole"
                ),

            "experience":
                self.member.get(
                    "yearsExperience"
                ),

            "status":
                self.member.get(
                    "status"
                ),

            "completed_days":
                self.get_completed_days(),

            "failed_days":
                self.get_failed_days(),

            "skipped_days":
                self.get_skipped_days(),

            "strong_days":
                self.get_strong_days(),

            "weak_days":
                self.get_weak_days(),

            "completion_ratio":
                self.completion_ratio(),

            "first_try_ratio":
                self.first_try_ratio(),

            "difficulty":
                self.determine_difficulty(),

            "recommended_questions":
                self.recommended_question_count(),

            "signals":
                self.signals
        }


# =====================================================
# Test
# =====================================================

if __name__ == "__main__":

    sample_candidate = {

        "member": {
            "id": "CAND-001",
            "name": "Sarah Johnson",
            "jobRole": "Senior Data Engineer",
            "yearsExperience": 9,
            "education": "MS Computer Science",
            "status": "COMPLETED"
        },

        "missions": [

            {
                "day": 1,
                "title": "Intro",
                "passed": True,
                "attempts": 1
            },

            {
                "day": 2,
                "title": "RAG",
                "passed": True,
                "attempts": 3
            },

            {
                "day": 3,
                "title": "Agents",
                "skipped": True
            }
        ],

        "signals": {
            "commitDays": 28,
            "missionsCompleted": 26,
            "missionsFirstTry": 18
        }
    }

    analyzer = CandidateAnalyzer(
        sample_candidate
    )

    result = analyzer.analyze()

    from pprint import pprint

    pprint(result)
