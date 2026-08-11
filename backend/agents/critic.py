import json

from backend.models.llm import get_llm


def critic_agent(state):

    llm = get_llm()

    question = state.get(
        "question",
        ""
    )

    draft_answer = state.get(
        "draft_answer",
        ""
    )

    retrieved_documents = state.get(
        "retrieved_documents",
        []
    )

    # ========================================================
    # LIMIT EVIDENCE
    # ========================================================

    # Critic ko saare retrieved chunks bhejne ki zaroorat nahi.
    # Sirf top 5 relevant chunks use karo.

    evidence = retrieved_documents[:5]

    evidence_text = ""

    for i, document in enumerate(
        evidence,
        start=1
    ):

        text = document.get(
            "text",
            ""
        )

        metadata = document.get(
            "metadata",
            {}
        )

        # Limit each chunk
        text = text[:1000]

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

{text}

"""

    # ========================================================
    # CRITIC PROMPT
    # ========================================================

    prompt = f"""
You are a strict research answer critic.

Evaluate the draft answer against the provided evidence.

QUESTION:
{question}

DRAFT ANSWER:
{draft_answer}

EVIDENCE:
{evidence_text}

Evaluate:

1. correctness
   Are the claims supported by the evidence?

2. completeness
   Does the answer sufficiently answer the question?

3. clarity
   Is the answer clear and well organized?

4. groundedness
   Are important factual claims traceable to the evidence?

Use scores from 1 to 5.

The answer PASSES if:
- correctness >= 4
- completeness >= 4
- clarity >= 4
- groundedness is true

Otherwise it FAILS.

If the answer fails, provide a short revision request.

Return ONLY valid JSON.

Format:

{{
    "correctness": 1,
    "completeness": 1,
    "clarity": 1,
    "groundedness": true,
    "overall": 1,
    "passed": true,
    "feedback": "Short feedback.",
    "revision_request": "Short revision request."
}}

Keep feedback under 30 words.
Keep revision_request under 30 words.
Do not provide reasoning.
Do not include markdown.
Do not include text outside JSON.
"""

    # ========================================================
    # CALL LLM
    # ========================================================

    response = llm.invoke(
        prompt
    )

    if hasattr(
        response,
        "content"
    ):
        content = response.content
    else:
        content = str(response)

    # ========================================================
    # PARSE JSON
    # ========================================================

    try:

        critique = json.loads(
            content
        )

    except json.JSONDecodeError:

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

                critique = json.loads(
                    content[
                        start:end + 1
                    ]
                )

            except json.JSONDecodeError:

                raise ValueError(
                    "Critic returned invalid JSON."
                )

        else:

            raise ValueError(
                "Critic did not return valid JSON."
            )

    # ========================================================
    # NORMALIZE VALUES
    # ========================================================

    correctness = int(
        critique.get(
            "correctness",
            0
        )
    )

    completeness = int(
        critique.get(
            "completeness",
            0
        )
    )

    clarity = int(
        critique.get(
            "clarity",
            0
        )
    )

    groundedness = bool(
        critique.get(
            "groundedness",
            False
        )
    )

    # ========================================================
    # CALCULATE OVERALL
    # ========================================================

    overall = round(
        (
            correctness
            + completeness
            + clarity
        ) / 3,
        2
    )

    # ========================================================
    # PASS / FAIL
    # ========================================================

    passed = (
        correctness >= 4
        and completeness >= 4
        and clarity >= 4
        and groundedness is True
    )

    feedback = critique.get(
        "feedback",
        ""
    )

    revision_request = critique.get(
        "revision_request",
        ""
    )

    # ========================================================
    # RETURN STATE UPDATE
    # ========================================================

    return {
        "critique": {
            "correctness": correctness,
            "completeness": completeness,
            "clarity": clarity,
            "groundedness": groundedness,
            "overall": overall,
            "passed": passed,
            "feedback": feedback
        },

        "revision_request": revision_request
    }