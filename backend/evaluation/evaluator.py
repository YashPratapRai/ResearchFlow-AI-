import json
from typing import Dict, Any

from backend.models.llm import get_llm


class ResearchEvaluator:

    def __init__(self):
        self.llm = get_llm()

    def evaluate(
        self,
        question: str,
        answer: str,
        evidence: list
    ) -> Dict[str, Any]:

        # ====================================================
        # Prepare LIMITED evidence
        # ====================================================

        evidence_text = ""

        # Only use top 5 retrieved evidence items
        evaluation_evidence = evidence[:5]

        for i, item in enumerate(
            evaluation_evidence,
            start=1
        ):

            metadata = item.get(
                "metadata",
                {}
            )

            text = item.get(
                "text",
                ""
            )

            # Limit each chunk size
            text = text[:1200]

            source = metadata.get(
                "source",
                "unknown"
            )

            page = metadata.get(
                "page",
                "unknown"
            )

            evidence_text += f"""
[EVIDENCE {i}]
Source: {source}
Page: {page}

Text:
{text}

"""

        # ====================================================
        # Evaluation Prompt
        # ====================================================

        prompt = f"""
You are an evaluation system for a research assistant.

Evaluate the generated answer strictly against the
provided evidence.

QUESTION:
{question}

ANSWER:
{answer}

EVIDENCE:
{evidence_text}

Evaluate the following dimensions:

1. correctness
   Are the important claims in the answer supported
   by the provided evidence?

2. completeness
   Does the answer sufficiently address the question?

3. clarity
   Is the answer clear, concise and understandable?

4. groundedness
   Can the important factual claims be traced to
   the provided evidence?

Give scores from 1 to 5.

Groundedness must be either true or false.

Return ONLY valid JSON.

Required format:

{{
    "correctness": 1,
    "completeness": 1,
    "clarity": 1,
    "groundedness": true,
    "feedback": "Short feedback under 30 words."
}}

Do not include markdown.
Do not include reasoning.
Do not include any text outside the JSON.
"""

        # ====================================================
        # Call LLM
        # ====================================================

        response = self.llm.invoke(
            prompt
        )

        if hasattr(
            response,
            "content"
        ):
            content = response.content
        else:
            content = str(response)

        # ====================================================
        # Parse JSON
        # ====================================================

        try:

            evaluation = json.loads(
                content
            )

        except json.JSONDecodeError:

            # Sometimes LLM may accidentally
            # wrap JSON in additional text.

            start = content.find(
                "{"
            )

            end = content.rfind(
                "}"
            )

            if (
                start != -1
                and end != -1
                and end > start
            ):

                try:

                    evaluation = json.loads(
                        content[
                            start:end + 1
                        ]
                    )

                except json.JSONDecodeError:

                    raise ValueError(
                        "Evaluator returned invalid JSON."
                    )

            else:

                raise ValueError(
                    "Evaluator did not return valid JSON."
                )

        # ====================================================
        # Validate scores
        # ====================================================

        correctness = evaluation.get(
            "correctness",
            0
        )

        completeness = evaluation.get(
            "completeness",
            0
        )

        clarity = evaluation.get(
            "clarity",
            0
        )

        groundedness = evaluation.get(
            "groundedness",
            False
        )

        # Make sure scores are numeric
        try:

            correctness = float(
                correctness
            )

            completeness = float(
                completeness
            )

            clarity = float(
                clarity
            )

        except (
            TypeError,
            ValueError
        ):

            raise ValueError(
                "Evaluator returned invalid score values."
            )

        # ====================================================
        # Clamp scores between 1 and 5
        # ====================================================

        correctness = max(
            1,
            min(
                5,
                correctness
            )
        )

        completeness = max(
            1,
            min(
                5,
                completeness
            )
        )

        clarity = max(
            1,
            min(
                5,
                clarity
            )
        )

        # ====================================================
        # Calculate Overall Score
        # ====================================================

        overall = round(
            (
                correctness
                + completeness
                + clarity
            ) / 3,
            2
        )

        # ====================================================
        # Return final evaluation
        # ====================================================

        return {
            "correctness": int(
                correctness
            ),

            "completeness": int(
                completeness
            ),

            "clarity": int(
                clarity
            ),

            "groundedness": bool(
                groundedness
            ),

            "overall": overall,

            "feedback": evaluation.get(
                "feedback",
                ""
            )
        }