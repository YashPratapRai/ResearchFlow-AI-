from backend.rag.retriever import ResearchRetriever
from backend.tools.memory_search import MemorySearchTool


def researcher_agent(state):

    question = state.get(
        "question",
        ""
    )

    queries = state.get(
        "research_queries",
        []
    )

    revision_request = state.get(
        "revision_request",
        ""
    )

    # ========================================================
    # Initialize search tools
    # ========================================================

    document_retriever = ResearchRetriever()

    memory_search = MemorySearchTool()

    # ========================================================
    # Build document retrieval queries
    # ========================================================

    retrieval_queries = list(queries)

    # If Critic rejected the previous answer,
    # search specifically for the missing information.
    if revision_request:

        retrieval_queries.append(
            f"""
            Find evidence needed to fix this problem:

            {revision_request}

            Original question:
            {question}
            """
        )

    # ========================================================
    # DOCUMENT SEARCH
    # ========================================================

    document_results = []

    for query in retrieval_queries:

        results = document_retriever.retrieve(
            query=query,
            top_k=5
        )

        for result in results:

            document_results.append({
                "type": "document",
                "query": query,
                "text": result["text"],
                "metadata": result["metadata"],
                "distance": result["distance"]
            })

    # ========================================================
    # MEMORY SEARCH
    # ========================================================

    memory_results = []

    # Search previous successful research
    memory_query = question

    memories = memory_search.search(
        query=memory_query,
        top_k=3
    )

    for memory in memories:

        memory_results.append({
            "type": "memory",
            "query": memory_query,
            "text": memory["text"],
            "metadata": memory["metadata"],
            "distance": memory["distance"]
        })

    # ========================================================
    # COMBINE DOCUMENT + MEMORY EVIDENCE
    # ========================================================

    retrieved_documents = (
        document_results +
        memory_results
    )

    # ========================================================
    # Return updated state
    # ========================================================

    return {
        "retrieved_documents": retrieved_documents
    }