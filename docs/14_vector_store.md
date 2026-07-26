# Vector Store

Stores text and lets you search for the most relevant pieces given a
question — the retrieval mechanism behind RAG.

---

## What it is

`InMemoryVectorStore` stores text chunks along with their **embeddings**
(numerical vectors that represent meaning), and can search that store for
the chunks most relevant to a query:

```python
store = InMemoryVectorStore()

store.add_texts([
    "The Eiffel Tower is located in Paris, France.",
    "Mount Everest is the tallest mountain on Earth.",
])

results = store.similarity_search("Where is the Eiffel Tower?", k=1)
print(results)
# [("The Eiffel Tower is located in Paris, France.", 0.9464)]
```

The number alongside each result is a similarity score — how closely that
text matches the meaning of the query, from -1 (opposite) to 1 (identical
direction in vector-space).

---

## Why it exists

An LLM only knows what it was trained on — it has no access to your
specific documents, your company's internal facts, or anything created
after its training cutoff. A vector store solves the *retrieval* half of
that problem: given a question, find which stored pieces of text are
actually relevant to it, so they can be handed to the LLM as context (see
`15_rag.md` for the full picture).

### Why cosine similarity, hand-written

Embeddings represent meaning as vectors — texts with similar meaning point
in similar directions in vector-space, regardless of length or magnitude.
Cosine similarity measures exactly that: the angle between two vectors,
not the distance between them.

```python
def _cosine_similarity(self, vec_a, vec_b):
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    magnitude_a = math.sqrt(sum(a * a for a in vec_a))
    magnitude_b = math.sqrt(sum(b * b for b in vec_b))
    return dot_product / (magnitude_a * magnitude_b)
```

This is written by hand on purpose — it's simple enough to implement
directly, and it's the actual mechanism that makes "search" work here.
Turning text into vectors (the embedding step) uses `OpenAIEmbeddings`
rather than being reimplemented — that part genuinely isn't worth
rebuilding from scratch, same reasoning as using LangChain's
`.bind_tools()` for Tool Calling.

---

## Basic usage

```python
from educhain.core.vectorstore import InMemoryVectorStore

store = InMemoryVectorStore()

store.add_texts([
    "Python is a popular programming language for AI and web development.",
    "The Great Wall of China is over 13,000 miles long.",
    "Deepak is building EduChain, a mini LangChain clone.",
])

results = store.similarity_search("What framework is Deepak building?", k=2)

for text, score in results:
    print(f"[{score:.4f}] {text}")
```

Notice the query never says "EduChain" — a good embedding matches
*meaning*, not just shared keywords.

---

## API Reference

### `InMemoryVectorStore(embedding_model=None)`

| Parameter | Type | Description |
|---|---|---|
| `embedding_model` | optional | Defaults to `OpenAIEmbeddings()` |

### `.add_texts(texts)`

| Parameter | Type | Description |
|---|---|---|
| `texts` | `list[str]` | Text chunks to embed and store |

**Raises:**
- `TypeError` — if `texts` isn't a list, or contains non-strings
- `ValueError` — if `texts` is empty

### `.similarity_search(query, k=3)`

| Parameter | Type | Description |
|---|---|---|
| `query` | `str` | The search query |
| `k` | `int` | How many top results to return (default 3) |

**Returns:** `list[tuple[str, float]]` — `(text, similarity_score)` pairs,
sorted highest similarity first

**Raises:**
- `TypeError` — if `query` isn't a string
- `ValueError` — if `query` is empty, or the store has nothing in it yet

---

## Full example

```python
from educhain.core.vectorstore import InMemoryVectorStore

store = InMemoryVectorStore()

store.add_texts([
    "NimbusTech was founded in 2021 by Ariana Kessler in Pune, India.",
    "NimbusTech's headquarters moved from Pune to Bangalore in 2023.",
    "NimbusTech's flagship product is CloudSprint, a deployment tool.",
    "CloudSprint supports deployments to AWS, Azure, and Google Cloud.",
])

query = "What cloud platforms does CloudSprint support?"
results = store.similarity_search(query, k=2)

for text, score in results:
    print(f"[{score:.4f}] {text}")

# [0.9282] CloudSprint supports deployments to AWS, Azure, and Google Cloud.
# [0.8832] NimbusTech's flagship product is CloudSprint, a deployment tool.
```

---

## Common pitfalls

**Searching an empty store.**
```python
store = InMemoryVectorStore()
store.similarity_search("anything")
# ValueError: Vector store is empty. Add some texts with add_texts() before searching.
```

**Confusing `embed_documents()` and `embed_query()`.**
Internally, `add_texts()` uses `embedding_model.embed_documents(texts)`
while `similarity_search()` uses `embedding_model.embed_query(query)` —
two different methods on the same model. Some embedding models are
trained to treat "things being searched for" slightly differently from
"the search itself," so using the matching method for each case gives
more accurate results. This is handled internally — just worth knowing
why two methods exist if you're extending this class.

**Nothing is persisted.**
Like `MessageHistory` (see `09_memory.md`), this store lives entirely in
memory — nothing is saved once your program exits. Fine for learning and
small-scale use; a production system would swap in a real vector database
(FAISS, Chroma, Pinecone) behind the same `similarity_search()` interface.

**Embedding calls cost money.**
Unlike most of EduChain's other components, `add_texts()` and
`similarity_search()` both make real calls to OpenAI's embeddings API —
a separate (small, but real) cost from chat completions. Worth knowing
before embedding a very large amount of text repeatedly.

---

## Where this is used next

A vector store on its own just finds relevant text — it doesn't answer
anything. The next doc, `15_rag.md`, covers what happens when you connect
retrieval to generation: Retrieval-Augmented Generation, where retrieved
context gets fed into a prompt to produce a grounded answer.