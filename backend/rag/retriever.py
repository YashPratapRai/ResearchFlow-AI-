from .vectorstore import ChromaVectorStore


class ResearchRetriever:

    def __init__(self):
        self.vectorstore = ChromaVectorStore()

    def retrieve(
        self,
        query: str,
        top_k: int = 5
    ):

        results = self.vectorstore.search(
            query=query,
            top_k=top_k
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieved_documents = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):
            retrieved_documents.append({
                "text": document,
                "metadata": metadata,
                "distance": distance
            })

        return retrieved_documents