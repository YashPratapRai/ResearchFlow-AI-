from sentence_transformers import SentenceTransformer


class EmbeddingModel:

    def __init__(self):
        self.model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )

        self.query_instruction = (
            "Represent this sentence for searching relevant passages: "
        )

    def embed_documents(
        self,
        texts: list[str]
    ) -> list[list[float]]:

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True
        )

        return embeddings.tolist()

    def embed_query(
        self,
        query: str
    ) -> list[float]:

        query_with_instruction = (
            self.query_instruction + query
        )

        embedding = self.model.encode(
            query_with_instruction,
            normalize_embeddings=True
        )

        return embedding.tolist()