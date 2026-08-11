from backend.memory.long_term import LongTermMemory


class MemorySearchTool:

    def __init__(self):
        self.memory = LongTermMemory()

    def search(
        self,
        query: str,
        top_k: int = 3
    ):
        """
        Search previous successful research
        stored in ChromaDB long-term memory.
        """

        results = self.memory.search(
            query=query,
            top_k=top_k
        )

        documents = results.get(
            "documents",
            [[]]
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]]
        )[0]

        distances = results.get(
            "distances",
            [[]]
        )[0]

        memories = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):

            memories.append({
                "text": document,
                "metadata": metadata,
                "distance": distance
            })

        return memories