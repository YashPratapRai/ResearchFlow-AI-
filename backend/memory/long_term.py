import uuid
from datetime import datetime

import chromadb

from backend.rag.embeddings import EmbeddingModel


class LongTermMemory:

    def __init__(self):

        # Persistent ChromaDB
        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        # Separate collection for successful research
        self.collection = self.client.get_or_create_collection(
            name="research_memory"
        )

        # Same embedding model used by RAG
        self.embedding_model = EmbeddingModel()

    # ========================================================
    # Save successful research
    # ========================================================

    def save(
        self,
        question: str,
        answer: str,
        research_notes=None
    ):

        if research_notes is None:
            research_notes = []

        # Convert research notes into text
        notes_text = "\n".join(
            str(note)
            for note in research_notes
        )

        memory_text = f"""
Question:
{question}

Answer:
{answer}

Research Notes:
{notes_text}
"""

        # Generate embedding
        embedding = self.embedding_model.embed_query(
            memory_text
        )

        memory_id = str(uuid.uuid4())

        self.collection.add(
            ids=[memory_id],

            embeddings=[embedding],

            documents=[memory_text],

            metadatas=[{
                "question": question,
                "created_at": datetime.now().isoformat()
            }]
        )

        return memory_id

    # ========================================================
    # Search previous research
    # ========================================================

    def search(
        self,
        query: str,
        top_k: int = 3
    ):

        embedding = self.embedding_model.embed_query(
            query
        )

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )

        return results