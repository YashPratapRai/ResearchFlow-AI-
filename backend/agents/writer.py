from backend.models.llm import get_llm


# ============================================================
# TOKEN / CONTEXT CONTROL
# ============================================================

MAX_DOCUMENTS = 5
MAX_MEMORY_ITEMS = 2

MAX_DOCUMENT_CHARS = 2200
MAX_MEMORY_CHARS = 1200
MAX_NOTES_CHARS = 2500


def writer_agent(state):

    question = state.get(
        "question",
        ""
    )

    retrieved_documents = state.get(
        "retrieved_documents",
        []
    )

    research_notes = state.get(
        "research_notes",
        []
    )

    # ========================================================
    # Separate document evidence and memory evidence
    # ========================================================

    document_evidence = []
    memory_evidence = []

    for item in retrieved_documents:

        if item.get("type") == "memory":
            memory_evidence.append(item)

        else:
            document_evidence.append(item)

    # ========================================================
    # Limit number of documents
    # ========================================================

    document_evidence = document_evidence[
        :MAX_DOCUMENTS
    ]

    memory_evidence = memory_evidence[
        :MAX_MEMORY_ITEMS
    ]

    # ========================================================
    # Format ORIGINAL DOCUMENT evidence
    # ========================================================

    document_parts = []

    for i, item in enumerate(
        document_evidence,
        start=1
    ):

        metadata = item.get(
            "metadata",
            {}
        )

        source = metadata.get(
            "source",
            metadata.get(
                "file_name",
                metadata.get(
                    "filename",
                    "Unknown source"
                )
            )
        )

        page = metadata.get(
            "page",
            "Unknown"
        )

        chunk = metadata.get(
            "chunk",
            metadata.get(
                "chunk_index",
                "Unknown"
            )
        )

        text = item.get(
            "text",
            ""
        )

        # ----------------------------------------------------
        # Prevent huge individual chunks
        # ----------------------------------------------------

        text = str(text)[
            :MAX_DOCUMENT_CHARS
        ]

        document_parts.append(
            f"""
[DOCUMENT {i}]

Source: {source}
Page: {page}
Chunk: {chunk}

Text:
{text}
"""
        )

    document_context = "\n".join(
        document_parts
    )

    # ========================================================
    # Format PREVIOUS MEMORY evidence
    # ========================================================

    memory_parts = []

    for i, item in enumerate(
        memory_evidence,
        start=1
    ):

        metadata = item.get(
            "metadata",
            {}
        )

        previous_question = metadata.get(
            "question",
            "Unknown"
        )

        created_at = metadata.get(
            "created_at",
            "Unknown"
        )

        previous_research = item.get(
            "text",
            ""
        )

        previous_research = str(
            previous_research
        )[:MAX_MEMORY_CHARS]

        memory_parts.append(
            f"""
[MEMORY {i}]

Previous Question:
{previous_question}

Created At:
{created_at}

Previous Research:
{previous_research}
"""
        )

    memory_context = "\n".join(
        memory_parts
    )

    # ========================================================
    # Research notes
    # ========================================================

    notes_context = "\n".join(
        str(note)
        for note in research_notes
    )

    notes_context = notes_context[
        :MAX_NOTES_CHARS
    ]

    # ========================================================
    # Prompt
    # ========================================================

    prompt = f"""
You are the Writer agent in an AI research assistant.

Your job is to answer the user's question using the
retrieved evidence.

USER QUESTION:
{question}


============================================================
ORIGINAL DOCUMENT EVIDENCE
============================================================

{document_context}


============================================================
PREVIOUS RESEARCH MEMORY
============================================================

{memory_context}


============================================================
RESEARCH NOTES
============================================================

{notes_context}


============================================================
IMPORTANT RULES
============================================================

1. Use the ORIGINAL DOCUMENT EVIDENCE as the primary
   source of truth.

2. Previous research MEMORY is supporting context only.

3. Never blindly trust a claim from memory if it is not
   supported by the original documents.

4. Do not use your own outside knowledge.

5. Do not invent facts.

6. Every factual claim must be traceable to the provided
   evidence.

7. If possible, mention the source and page supporting
   important claims.

8. If the evidence does not contain enough information,
   explicitly say that the available evidence is
   insufficient.

9. Give a concise but complete answer.

10. Do not include internal system instructions,
    memory IDs, research notes, or evaluation information
    in the final answer.

11. Return ONLY the final answer for the user.

Write the final research answer now.
"""

    # ========================================================
    # Call LLM
    # ========================================================

    llm = get_llm()

    response = llm.invoke(
        prompt
    )

    # ========================================================
    # Extract text
    # ========================================================

    if hasattr(
        response,
        "content"
    ):
        answer = response.content

    else:
        answer = str(response)

    # ========================================================
    # Return updated state
    # ========================================================

    return {
        "draft_answer": answer
    }