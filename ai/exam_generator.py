"""
PHISHVERSE – ai/exam_generator.py
Generates adaptive final-exam topic distributions weighted by bias profile.

Distribution logic:
  1. Every bias axis receives BASE_PER_AXIS questions as a floor.
  2. The remaining TOTAL_QUESTIONS - (BASE_PER_AXIS * 4) slots are allocated
     proportionally to each axis's bias score.
  3. Any rounding remainder is awarded to the highest-bias axis.
  4. If all biases are 0 (perfect run), the extra slots are split evenly
     (the proportional step safely divides by total_b = 1 due to guard).

Example (urgency_bias=3, authority_bias=2, reward_bias=0, fear_bias=0):
  total_b = 5, extra = 2
  urgency  gets BASE + round(3/5 * 2) = 2 + 1 = 3 questions
  authority gets BASE + round(2/5 * 2) = 2 + 1 = 3 questions
  reward   → 2 (base only)
  fear     → 2 (base only)
  total = 10 ✓

The generated_topics list is consumed by QuestionEngine.select_questions()
to pick questions in the correct per-topic proportions.
"""

_BIAS_KEYS      = ("urgency", "authority", "reward", "fear")
BASE_PER_AXIS   = 2    # minimum questions per bias axis
TOTAL_QUESTIONS = 10   # target exam length


def _bias(data: dict, key: str) -> int:
    return int(data.get(f"{key}_bias", data.get(key, 0)))


class ExamGenerator:
    """
    Produces a bias-weighted exam profile for adaptive question selection.
    """

    def generate_profile(self, bias_profile: dict, employee_id: str = "") -> dict:
        """
        Compute topic distribution for the final exam.

        Returns:
        {
            "employee_id":        str,
            "total_questions":    int,
            "topic_distribution": {"urgency": int, "authority": int, ...},
            "generated_topics":   ["urgency", "urgency", "authority", ...],
        }
        """
        biases  = {k: _bias(bias_profile, k) for k in _BIAS_KEYS}
        total_b = sum(biases.values()) or 1   # guard against all-zero (perfect run)
        extra   = TOTAL_QUESTIONS - (BASE_PER_AXIS * len(_BIAS_KEYS))

        dist  = {k: BASE_PER_AXIS for k in _BIAS_KEYS}
        rem   = extra
        order = sorted(biases.items(), key=lambda kv: kv[1], reverse=True)

        for bias, score in order:
            if rem <= 0:
                break
            alloc      = min(rem, round((score / total_b) * extra))
            dist[bias] += alloc
            rem        -= alloc

        if rem > 0:
            dist[order[0][0]] += rem   # give leftovers to highest-bias axis

        topics = []
        for k in _BIAS_KEYS:
            topics.extend([k] * dist[k])

        return {
            "employee_id":        employee_id,
            "total_questions":    sum(dist.values()),
            "topic_distribution": dict(dist),
            "generated_topics":   topics,
        }
