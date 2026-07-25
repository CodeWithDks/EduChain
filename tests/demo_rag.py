"""
demo_rag.py

Author: Deepak Singh (github.com/CodeWithDks)
Project: EduChain — a mini LangChain clone, built for learning

Demonstrates RAG (Retrieval-Augmented Generation) — answering
questions using context retrieved from a vector store, instead
of relying only on what the LLM already knows.

Run directly:
    python demo_rag.py
"""

from dotenv import load_dotenv

from educhain.models.llm import ChatModel
from educhain.prompts.prompt import PromptTemplate
from educhain.output_parsers.parser import StringOutputParser
from educhain.core.vectorstore import InMemoryVectorStore
from educhain.core.rag import RAGChain

load_dotenv()


def section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# ---------------------------------------------------------------
# Build a small knowledge base the LLM couldn't possibly know —
# made-up facts about a fictional company, so we can PROVE the
# answer is coming from retrieval, not the model's own training
# ---------------------------------------------------------------
def build_knowledge_base():

    store = InMemoryVectorStore()

    store.add_texts([
        "NimbusTech was founded in 2021 by Ariana Kessler in Pune, India.",
        "NimbusTech's flagship product is CloudSprint, a deployment tool for small teams.",
        "NimbusTech has 42 employees as of 2025.",
        "CloudSprint supports deployments to AWS, Azure, and Google Cloud.",
        "NimbusTech's headquarters moved from Pune to Bangalore in 2023.",
        "The CEO of NimbusTech, Ariana Kessler, previously worked at a fintech startup.",
    ])

    return store


# ---------------------------------------------------------------
# Build the RAG chain — vectorstore + existing prompt|model|parser
# ---------------------------------------------------------------
def build_rag_chain(store):

    model = ChatModel()
    parser = StringOutputParser()

    prompt = PromptTemplate(
        template=(
            "Answer the question using ONLY the context below. "
            "If the answer isn't in the context, say you don't know.\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n"
            "Answer:"
        ),
        input_variables=["context", "question"],
    )

    chain = prompt | model | parser

    return RAGChain(vectorstore=store, chain=chain, k=3)


# ---------------------------------------------------------------
# 1. Ask a question that's clearly answerable from the knowledge base
# ---------------------------------------------------------------
def demo_basic_rag():
    section("1. RAG answers using retrieved facts (LLM couldn't know this)")

    store = build_knowledge_base()
    rag = build_rag_chain(store)

    question = "Who founded NimbusTech and where is it based now?"
    answer = rag.invoke(question)

    print(f"Q: {question}")
    print(f"A: {answer}")


# ---------------------------------------------------------------
# 2. Inspect exactly what was retrieved, separate from generation
# ---------------------------------------------------------------
def demo_inspect_retrieval():
    section("2. Inspecting retrieved chunks before generation")

    store = build_knowledge_base()
    rag = build_rag_chain(store)

    question = "What cloud platforms does CloudSprint support?"
    chunks = rag.get_relevant_chunks(question)

    print(f"Q: {question}\n")
    print("Retrieved chunks:")
    for text, score in chunks:
        print(f"  [{score:.4f}] {text}")

    answer = rag.invoke(question)
    print(f"\nFinal answer: {answer}")


# ---------------------------------------------------------------
# 3. Ask something NOT in the knowledge base — should say "don't know"
# ---------------------------------------------------------------
def demo_out_of_context_question():
    section("3. Question with no answer in the knowledge base")

    store = build_knowledge_base()
    rag = build_rag_chain(store)

    question = "What is NimbusTech's annual revenue?"
    answer = rag.invoke(question)

    print(f"Q: {question}")
    print(f"A: {answer}")
    print("\n(Expected: model should admit it doesn't know, not make something up)")


# ---------------------------------------------------------------
# 4. Validation errors
# ---------------------------------------------------------------
def demo_rag_validation():
    section("4. RAGChain validation")

    store = build_knowledge_base()

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template="{context}\n{question}",
        input_variables=["context", "question"],
    )
    chain = prompt | model | parser

    # bad chain type
    try:
        RAGChain(vectorstore=store, chain="not a runnable")
        print("❌ FAILED: should have raised TypeError")
    except TypeError as e:
        print(f"✅ Correctly raised TypeError: {e}")

    # bad vectorstore type
    try:
        RAGChain(vectorstore="not a vectorstore", chain=chain)
        print("❌ FAILED: should have raised TypeError")
    except TypeError as e:
        print(f"✅ Correctly raised TypeError: {e}")

    # empty question
    rag = RAGChain(vectorstore=store, chain=chain)
    try:
        rag.invoke("")
        print("❌ FAILED: should have raised ValueError")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")


# ---------------------------------------------------------------
# Run all RAG demos
# ---------------------------------------------------------------
if __name__ == "__main__":

    demos = [
        demo_basic_rag,
        demo_inspect_retrieval,
        demo_out_of_context_question,
        demo_rag_validation,
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"⚠️  {demo.__name__} failed: {type(e).__name__}: {e}")

    print("\n" + "=" * 60)
    print("✨ EduChain — RAG demoed")
    print("=" * 60)