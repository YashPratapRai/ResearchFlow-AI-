import json

from backend.models.llm import get_llm


def planner_agent(state):

    question = state["question"]

    llm = get_llm()

    prompt = f"""
You are the Planner of a multi-agent research assistant.

Analyze the user's research question and break it into
2 to 4 focused research queries.

User question:
{question}

Return ONLY valid JSON.

Format:

{{
    "intent": "single_doc",
    "queries": [
        "query 1",
        "query 2",
        "query 3"
    ]
}}

Possible intents:

- single_doc
- comparison
- synthesis
- followup

Do not answer the question.
Only create the research plan.
"""

    response = llm.invoke(prompt)

    content = response.content.strip()

    # Remove markdown code fences if the model adds them
    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    plan = json.loads(content)

    return {
        "plan": plan,
        "research_queries": plan["queries"]
    }