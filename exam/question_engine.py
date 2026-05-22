"""
PHISHVERSE – exam/question_engine.py
Adaptive question selection from question_bank.json.

Selection strategy:
  • Primary weakness category receives 4 of 10 questions.
  • Remaining 3 categories receive 2 questions each.
  • If no clear primary, distribution is 3-3-2-2.
  • Final order is shuffled so the primary category is not clustered.

Weakness → category mapping:
  "Urgency Manipulation" → "urgency"
  "Authority Phishing"   → "authority"
  "Reward Lures"         → "reward"
  "Fear Tactics"         → "fear"
"""

import json
import random
from pathlib import Path

BANK_PATH = Path(__file__).parent / "question_bank.json"

# Map SemesterReport weakness names to question categories
WEAKNESS_TO_CAT: dict[str, str] = {
    "Urgency Manipulation": "urgency",
    "Authority Phishing":   "authority",
    "Reward Lures":         "reward",
    "Fear Tactics":         "fear",
}

CATEGORIES = ["urgency", "authority", "reward", "fear"]


class QuestionEngine:
    """
    Loads the question bank once and serves adaptive question sets.
    """

    def __init__(self):
        self._bank: list[dict] = self._load()
        self._by_category: dict[str, list] = {}
        for q in self._bank:
            cat = q.get("category", "general")
            self._by_category.setdefault(cat, []).append(q)

    # ── Internal ──────────────────────────────────────────────────────────────

    @staticmethod
    def _load() -> list:
        if not BANK_PATH.exists():
            print(f"[QuestionEngine] WARNING: question_bank.json not found at {BANK_PATH}")
            return []
        with open(BANK_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("questions", [])

    # ── Public API ────────────────────────────────────────────────────────────

    def select_questions(self, primary_weakness: str = "", n: int = 10) -> list[dict]:
        """
        Adaptively select n questions, weighting toward the primary weakness category.

        Args:
            primary_weakness: e.g. "Authority Phishing" from SemesterReport
            n:                total questions to return (default 10)

        Returns:
            Shuffled list of question dicts.
        """
        primary_cat = WEAKNESS_TO_CAT.get(primary_weakness, "")

        if primary_cat and primary_cat in CATEGORIES:
            distribution = {primary_cat: 4}
            for c in CATEGORIES:
                if c != primary_cat:
                    distribution[c] = 2          # 4 + 2+2+2 = 10
        else:
            # No clear primary — balanced 3-3-2-2
            distribution = {
                CATEGORIES[0]: 3, CATEGORIES[1]: 3,
                CATEGORIES[2]: 2, CATEGORIES[3]: 2,
            }

        selected: list[dict] = []
        for cat, count in distribution.items():
            pool = self._by_category.get(cat, [])
            take = min(count, len(pool))
            if take:
                selected.extend(random.sample(pool, take))

        random.shuffle(selected)
        return selected[:n]

    @property
    def total_questions(self) -> int:
        return len(self._bank)

    # ── Static helpers ────────────────────────────────────────────────────────

    @staticmethod
    def correct_index(question: dict) -> int:
        """Convert answer letter ('A'/'B'/'C'/'D') to 0-based option index."""
        ans = question.get("answer", "A").upper()
        return ord(ans) - ord("A")

    @staticmethod
    def score(questions: list[dict], answers: list[int]) -> dict:
        """
        Score a completed exam.

        Args:
            questions: list of question dicts (in order presented)
            answers:   list of selected option indices (0-3) per question

        Returns:
            {
              "score":       int (0-100),
              "correct":     int,
              "total":       int,
              "passed":      bool,
              "by_category": { category: {"correct": int, "total": int} }
            }
        """
        correct_total = 0
        by_cat: dict[str, dict] = {}

        for i, q in enumerate(questions):
            cat         = q.get("category", "general")
            correct_idx = QuestionEngine.correct_index(q)
            selected    = answers[i] if i < len(answers) else -1
            is_correct  = (selected == correct_idx)

            by_cat.setdefault(cat, {"correct": 0, "total": 0})
            by_cat[cat]["total"] += 1
            if is_correct:
                correct_total += 1
                by_cat[cat]["correct"] += 1

        total  = len(questions)
        score  = round(correct_total / total * 100) if total else 0
        passed = score >= 70

        return {
            "score":       score,
            "correct":     correct_total,
            "total":       total,
            "passed":      passed,
            "by_category": by_cat,
        }
