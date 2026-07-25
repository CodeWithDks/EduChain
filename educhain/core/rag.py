"""
rag.py

Author: Deepak Singh (github.com/CodeWithDks)
Project: EduChain — a mini LangChain clone, built for learning

Contains the RAGChain class.

Responsibility:
---------------
Retrieval-Augmented Generation — answer a question using
relevant context pulled from a vector store, instead of relying
only on whatever the LLM already "knows."

This is NOT a new primitive. It's a pattern built entirely from
pieces you've already built: InMemoryVectorStore + PromptTemplate
+ your existing prompt | model | parser chain.

Flow:

question (string)
      |
      v
similarity_search()  -->  relevant text chunks
      |
      v
inject chunks as "context" into the input dict
      |
      v
existing chain.invoke({"context": ..., "question": ...})
      |
      v
answer (whatever the chain's parser returns)
"""

from educhain.core.runnable import Runnable


class RAGChain(Runnable):
    """
    Wraps a vector store + an existing chain together, so a single
    .invoke(question) call does retrieval AND generation.

    The wrapped chain's PromptTemplate MUST have "context" and
    "question" as input variables — that's the contract RAGChain
    expects. See demo_rag.py for a working example template.
    """

    def __init__(self, vectorstore, chain, k=3):

        if not isinstance(chain, Runnable):
            raise TypeError(
                f"RAGChain expects a Runnable chain, but got {type(chain).__name__}. "
                "Pass something like: PromptTemplate | ChatModel | StringOutputParser"
            )

        # duck-typed check instead of isinstance, so RAGChain works with
        # any vector store that implements similarity_search() — not
        # just InMemoryVectorStore specifically
        if not hasattr(vectorstore, "similarity_search"):
            raise TypeError(
                f"RAGChain expects a vector store with a similarity_search() method, "
                f"but got {type(vectorstore).__name__}."
            )

        self.vectorstore = vectorstore
        self.chain = chain
        self.k = k

    def invoke(self, question):

        if not isinstance(question, str):
            raise TypeError(
                f"RAGChain expects a string question, but got {type(question).__name__}."
            )

        if question.strip() == "":
            raise ValueError(
                "Question cannot be empty."
            )

        # ---- Retrieve relevant chunks ----
        results = self.vectorstore.similarity_search(question, k=self.k)

        # results is a list of (text, score) tuples — we only need
        # the text for the prompt, scores were just for our own inspection
        context = "\n".join(text for text, score in results)

        # ---- Generate the answer using the retrieved context ----
        return self.chain.invoke({
            "context": context,
            "question": question,
        })

    def get_relevant_chunks(self, question, k=None):
        """
        Lets you inspect what was retrieved without running the full
        chain — useful for debugging "why did the LLM answer that way."
        """
        return self.vectorstore.similarity_search(question, k=k or self.k)

    def __repr__(self):
        return f"RAGChain(k={self.k}, chain={self.chain!r})"