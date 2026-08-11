import json

from backend.graph.workflow import build_graph
from backend.evaluation.evaluator import ResearchEvaluator


MAX_REVISIONS = 2


def load_questions():

    with open(
        "evaluation_questions.json",
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def create_initial_state(question):

    return {
        "question": question,
        "plan": {},
        "research_queries": [],
        "retrieved_documents": [],
        "research_notes": [],
        "draft_answer": "",
        "critique": {},
        "revision_request": "",
        "revision_count": 0,
        "final_answer": ""
    }


def main():

    questions = load_questions()

    graph = build_graph()

    evaluator = ResearchEvaluator()

    results = []

    print("\n" + "=" * 80)
    print("RESEARCH ASSISTANT EVALUATION")
    print("=" * 80)

    print(
        f"\nQuestions to evaluate: {len(questions)}"
    )

    # ========================================================
    # Run every question through the complete graph
    # ========================================================

    for index, item in enumerate(
        questions,
        start=1
    ):

        question = item["question"]

        print("\n" + "-" * 80)
        print(
            f"QUESTION {index}/{len(questions)}"
        )
        print("-" * 80)

        print(question)

        initial_state = create_initial_state(
            question
        )

        # ----------------------------------------------------
        # Run LangGraph
        # ----------------------------------------------------

        state = graph.invoke(
            initial_state
        )

        answer = state.get(
            "final_answer",
            state.get(
                "draft_answer",
                ""
            )
        )

        evidence = state.get(
            "retrieved_documents",
            []
        )

        critique = state.get(
            "critique",
            {}
        )

        revision_count = state.get(
            "revision_count",
            0
        )

        # ----------------------------------------------------
        # Evaluate generated answer
        # ----------------------------------------------------

        evaluation = evaluator.evaluate(
            question=question,
            answer=answer,
            evidence=evidence
        )

        # ----------------------------------------------------
        # Add graph information
        # ----------------------------------------------------

        evaluation["question"] = question

        evaluation["revision_count"] = (
            revision_count
        )

        evaluation["critic_passed"] = (
            critique.get(
                "passed",
                False
            )
        )

        evaluation["evidence_count"] = len(
            evidence
        )

        # ----------------------------------------------------
        # Store result
        # ----------------------------------------------------

        results.append(
            evaluation
        )

        # ----------------------------------------------------
        # Print result
        # ----------------------------------------------------

        print(
            f"\nCorrectness : "
            f"{evaluation['correctness']}/5"
        )

        print(
            f"Completeness: "
            f"{evaluation['completeness']}/5"
        )

        print(
            f"Clarity     : "
            f"{evaluation['clarity']}/5"
        )

        print(
            f"Groundedness: "
            f"{evaluation['groundedness']}"
        )

        print(
            f"Overall     : "
            f"{evaluation['overall']}/5"
        )

        print(
            f"Revisions   : "
            f"{revision_count}"
        )

        print(
            f"Evidence    : "
            f"{len(evidence)}"
        )

    # ========================================================
    # Aggregate metrics
    # ========================================================

    if not results:
        print("\nNo evaluation results.")
        return

    average_correctness = (
        sum(
            result["correctness"]
            for result in results
        )
        / len(results)
    )

    average_completeness = (
        sum(
            result["completeness"]
            for result in results
        )
        / len(results)
    )

    average_clarity = (
        sum(
            result["clarity"]
            for result in results
        )
        / len(results)
    )

    average_overall = (
        sum(
            result["overall"]
            for result in results
        )
        / len(results)
    )

    grounded_count = sum(
        1
        for result in results
        if result["groundedness"]
    )

    passed_count = sum(
        1
        for result in results
        if result["critic_passed"]
    )

    total_revisions = sum(
        result["revision_count"]
        for result in results
    )

    groundedness_rate = (
        grounded_count
        / len(results)
        * 100
    )

    pass_rate = (
        passed_count
        / len(results)
        * 100
    )

    average_revisions = (
        total_revisions
        / len(results)
    )

    # ========================================================
    # Final report
    # ========================================================

    print("\n\n" + "=" * 80)
    print("FINAL EVALUATION REPORT")
    print("=" * 80)

    print(
        f"\nQuestions Evaluated : "
        f"{len(results)}"
    )

    print(
        f"\nAverage Correctness : "
        f"{average_correctness:.2f}/5"
    )

    print(
        f"Average Completeness: "
        f"{average_completeness:.2f}/5"
    )

    print(
        f"Average Clarity     : "
        f"{average_clarity:.2f}/5"
    )

    print(
        f"Average Overall     : "
        f"{average_overall:.2f}/5"
    )

    print(
        f"\nGroundedness Rate   : "
        f"{groundedness_rate:.1f}%"
    )

    print(
        f"Critic Pass Rate    : "
        f"{pass_rate:.1f}%"
    )

    print(
        f"Average Revisions   : "
        f"{average_revisions:.2f}"
    )

    print("\n" + "=" * 80)

    # ========================================================
    # Save detailed results
    # ========================================================

    with open(
        "evaluation_results.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        "\nDetailed results saved to:"
        " evaluation_results.json"
    )


if __name__ == "__main__":
    main()