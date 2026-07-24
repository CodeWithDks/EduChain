"""
demo_vectorstore.py

Author: Deepak Singh (github.com/CodeWithDks)
Project: EduChain — a mini LangChain clone, built for learning

Demonstrates InMemoryVectorStore — storing text chunks and
retrieving the most relevant ones for a given query.

Run directly:
    python demo_vectorstore.py
"""

from dotenv import load_dotenv

from educhain.core.vectorstore import InMemoryVectorStore

load_dotenv()


def section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# ---------------------------------------------------------------
# 1. Store a handful of unrelated facts, search a related question
# ---------------------------------------------------------------
def demo_basic_search():
    section("1. Basic similarity search — mixed topics")

    store = InMemoryVectorStore()

    store.add_texts([
        "The Eiffel Tower is located in Paris, France.",
        "Mount Everest is the tallest mountain on Earth.",
        "Python is a popular programming language for AI and web development.",
        "The Great Wall of China is over 13,000 miles long.",
        "Deepak is building EduChain, a mini LangChain clone.",
    ])

    query = "Where is the Eiffel Tower located?"
    results = store.similarity_search(query, k=2)

    print(f"Query: {query}\n")
    for text, score in results:
        print(f"  [{score:.4f}] {text}")


# ---------------------------------------------------------------
# 2. Search where the top result should clearly be about EduChain
# ---------------------------------------------------------------
def demo_project_specific_search():
    section("2. Searching for a specific, narrow topic")

    store = InMemoryVectorStore()

    store.add_texts([
        "The Eiffel Tower is located in Paris, France.",
        "Mount Everest is the tallest mountain on Earth.",
        "Python is a popular programming language for AI and web development.",
        "Deepak is building EduChain, a mini LangChain clone, from scratch.",
        "EduChain supports streaming, async execution, and tool calling.",
    ])

    query = "What framework is Deepak building?"
    results = store.similarity_search(query, k=3)

    print(f"Query: {query}\n")
    for text, score in results:
        print(f"  [{score:.4f}] {text}")


# ---------------------------------------------------------------
# 3. Validation — empty store, empty query, wrong types
# ---------------------------------------------------------------
def demo_validation():
    section("3. Validation checks")

    store = InMemoryVectorStore()

    # searching an empty store
    try:
        store.similarity_search("anything")
        print("❌ FAILED: should have raised ValueError")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")

    # adding a non-list
    try:
        store.add_texts("just one string, not a list")
        print("❌ FAILED: should have raised TypeError")
    except TypeError as e:
        print(f"✅ Correctly raised TypeError: {e}")

    # adding an empty list
    try:
        store.add_texts([])
        print("❌ FAILED: should have raised ValueError")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")

    # now add something real, then try an empty query
    store.add_texts(["A valid fact to search against."])

    try:
        store.similarity_search("")
        print("❌ FAILED: should have raised ValueError")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")


# ---------------------------------------------------------------
# Run all vector store demos
# ---------------------------------------------------------------
if __name__ == "__main__":

    demos = [
        demo_basic_search,
        demo_project_specific_search,
        demo_validation,
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"⚠️  {demo.__name__} failed: {type(e).__name__}: {e}")

    print("\n" + "=" * 60)
    print("✨ EduChain — vector store demoed")
    print("=" * 60)