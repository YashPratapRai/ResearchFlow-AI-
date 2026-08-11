import chromadb

from .embeddings import EmbeddingModel


class ChromaVectorStore:

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="research_documents",
            metadata={"hnsw:space": "cosine"}
        )

        self.embedding_model = EmbeddingModel()

    def add_documents(self, documents: list[dict]):

        texts = [
            document["text"]
            for document in documents
        ]

        embeddings = self.embedding_model.embed_documents(
            texts
        )

        ids = [
            f"{document['metadata']['source']}_"
            f"{document['metadata']['page']}_"
            f"{document['metadata']['chunk']}"
            for document in documents
        ]

        metadatas = [
            document["metadata"]
            for document in documents
        ]

        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(self, query: str, top_k: int = 5):

        query_embedding = self.embedding_model.embed_query(
            query
        )

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        return results