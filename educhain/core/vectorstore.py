"""
vectorstore.py

Author: Deepak Singh (github.com/CodeWithDks)
Project: EduChain — a mini LangChain clone, built for learning

Contains the InMemoryVectorStore class.

Responsibility:
---------------
Store text chunks along with their embeddings, and let you
search for the most relevant chunks given a query.

This is the foundation RAG is built on: retrieve the most
relevant pieces of text, then stuff them into a prompt so the
LLM answers using real, specific information instead of
whatever it happens to remember.

We use OpenAIEmbeddings to turn text into vectors (no reason
to reimplement an embedding model from scratch), but the actual
similarity search — the "which text is closest to my question"
logic — is hand-written here, since that's the part worth
understanding.
"""

import math
from langchain_openai import OpenAIEmbeddings


class InMemoryVectorStore:
    """
    A simple, in-memory store for text + embeddings.

    Not persisted anywhere — once the program ends, everything
    added here is gone. Good enough for learning/testing.
    A real app would swap this for a proper vector DB
    (FAISS, Chroma, Pinecone, etc.) later.
    """

    def __init__(self, embedding_model=None):

        # if user didn't pass an embedding model, fall back to default
        self.embedding_model = embedding_model or OpenAIEmbeddings()

        # parallel lists — texts[i] corresponds to vectors[i]
        self.texts = []
        self.vectors = []

    def add_texts(self, texts):
        """
        Embeds and stores a list of text chunks.

        Example:
            store.add_texts([
                "The Eiffel Tower is in Paris.",
                "Mount Everest is the tallest mountain."
            ])
        """

        if not isinstance(texts, list):
            raise TypeError(
                f"add_texts expects a list of strings, but got {type(texts).__name__}."
            )

        if len(texts) == 0:
            raise ValueError(
                "add_texts requires at least one text chunk."
            )

        for text in texts:
            if not isinstance(text, str):
                raise TypeError(
                    f"Every item in texts must be a string, but got {type(text).__name__}."
                )

        # embed_documents() sends all texts in one batch call —
        # much faster than embedding one at a time in a loop
        new_vectors = self.embedding_model.embed_documents(texts)

        self.texts.extend(texts)
        self.vectors.extend(new_vectors)

    def _cosine_similarity(self, vec_a, vec_b):
        """
        Measures how similar two vectors are, from -1 (opposite)
        to 1 (identical direction). This is the actual "search"
        mechanism — embeddings that mean similar things end up
        pointing in similar directions in vector space.

        Formula: (A . B) / (|A| * |B|)
        """

        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))

        magnitude_a = math.sqrt(sum(a * a for a in vec_a))
        magnitude_b = math.sqrt(sum(b * b for b in vec_b))

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (magnitude_a * magnitude_b)

    def similarity_search(self, query, k=3):
        """
        Finds the k most relevant stored texts for a given query.

        Example:
            results = store.similarity_search("Where is the Eiffel Tower?", k=2)
        """

        if not isinstance(query, str):
            raise TypeError(
                f"similarity_search expects a string query, but got {type(query).__name__}."
            )

        if query.strip() == "":
            raise ValueError(
                "Query cannot be empty."
            )

        if len(self.texts) == 0:
            raise ValueError(
                "Vector store is empty. Add some texts with add_texts() before searching."
            )

        # embed_query() is used here instead of embed_documents() —
        # some embedding models handle queries slightly differently
        # from documents, so LangChain gives us a separate method
        query_vector = self.embedding_model.embed_query(query)

        # score every stored text against the query
        scored = [
            (text, self._cosine_similarity(query_vector, vector))
            for text, vector in zip(self.texts, self.vectors)
        ]

        # highest similarity first
        scored.sort(key=lambda pair: pair[1], reverse=True)

        # return just the top k texts (with scores, so users can
        # inspect confidence if they want)
        return scored[:k]

    def __repr__(self):
        return f"InMemoryVectorStore({len(self.texts)} texts stored)"