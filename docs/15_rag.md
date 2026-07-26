# RAG (Retrieval-Augmented Generation)

Answers a question using relevant context retrieved from a vector store,
instead of relying only on what the LLM already knows.

---

## What it is

`RAGChain` connects two things you've already built: an `InMemoryVectorStore`
(see `14_vector_store.md`) and an existing `prompt | model | parser` chain.
Given a question, it retrieves the most relevant stored text, injects it
into the prompt as context, and lets the chain generate an answer grounded
in that context:

```python
answer = rag.invoke("Where is NimbusTech headquartered now?")
# "NimbusTech is headquartered in Bangalore, India."
```

---

## Why it exists — and why it's not really a new mechanism

This is the most important thing to understand about RAG in EduChain:
**it isn't a new primitive.** It's a *pattern*, assembled entirely from
pieces already built:

```
question
   │
   ▼
similarity_search()  →  relevant text chunks       (from 14_vector_store.md)
   │
   ▼
inject as "context" into the input dict
   │
   ▼
existing chain.invoke({"context": ..., "question": ...})   (from 05_runnable_sequence.md)
   │
   ▼
answer
```

`RAGChain` itself is small — its `.invoke()` method is essentially: call
`similarity_search()`, join the results into a string, hand that to the
wrapped chain. Everything that makes it work correctly (retrieval quality,
prompt formatting, generation) was already built and tested in earlier
layers.

### Why RAGChain inherits from Runnable

Unlike `Tool` (which genuinely doesn't fit the single-input shape — see
`13_tool_calling.md`), `RAGChain.invoke(question)` still takes one input
and returns one output. It fits the `Runnable` contract cleanly, which
means it could even be composed inside a `RunnableSequence` or
`RunnableParallel` later — e.g. comparing RAG-based answers against
non-RAG answers side by side.

---

## Basic usage

```python
from educhain.core.vectorstore import InMemoryVectorStore
from educhain.core.rag import RAGChain
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import StringOutputParser

store = InMemoryVectorStore()
store.add_texts([
    "NimbusTech was founded in 2021 by Ariana Kessler in Pune, India.",
    "NimbusTech's headquarters moved from Pune to Bangalore in 2023.",
])

prompt = PromptTemplate(
    template=(
        "Answer using ONLY the context below. "
        "If the answer isn't in the context, say you don't know.\n\n"
        "Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    ),
    input_variables=["context", "question"],
)

chain = prompt | ChatModel() | StringOutputParser()
rag = RAGChain(vectorstore=store, chain=chain, k=3)

print(rag.invoke("Who founded NimbusTech?"))
```

The prompt's grounding instruction ("If the answer isn't in the context,
say you don't know") matters a lot — see pitfalls below.

---

## API Reference

### `RAGChain(vectorstore, chain, k=3)`

| Parameter | Type | Description |
|---|---|---|
| `vectorstore` | any object with `.similarity_search()` | Duck-typed, not restricted to `InMemoryVectorStore` specifically |
| `chain` | `Runnable` | Must have a `PromptTemplate` with `context` and `question` as input variables |
| `k` | `int` | How many chunks to retrieve per question (default 3) |

**Raises at construction:**
- `TypeError` — if `chain` isn't a `Runnable`
- `TypeError` — if `vectorstore` doesn't have a `similarity_search` method

### `.invoke(question)`

**Returns:** whatever the wrapped chain's final step returns (typically a
string, if the chain ends in `StringOutputParser`)

**Raises:**
- `TypeError` — if `question` isn't a string
- `ValueError` — if `question` is empty

### `.get_relevant_chunks(question, k=None)`

Runs retrieval only, without generation — useful for debugging what
context an answer was actually based on.

**Returns:** same as `InMemoryVectorStore.similarity_search()` —
`list[tuple[str, float]]`

---

## Full example — with retrieval inspection

```python
from educhain.core.vectorstore import InMemoryVectorStore
from educhain.core.rag import RAGChain
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import StringOutputParser

store = InMemoryVectorStore()
store.add_texts([
    "CloudSprint supports deployments to AWS, Azure, and Google Cloud.",
    "NimbusTech's flagship product is CloudSprint, a deployment tool.",
    "NimbusTech was founded in 2021 by Ariana Kessler.",
])

prompt = PromptTemplate(
    template=(
        "Answer using ONLY the context below. "
        "If the answer isn't in the context, say you don't know.\n\n"
        "Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    ),
    input_variables=["context", "question"],
)
chain = prompt | ChatModel() | StringOutputParser()
rag = RAGChain(vectorstore=store, chain=chain, k=2)

question = "What cloud platforms does CloudSprint support?"

# Inspect retrieval before generation runs
chunks = rag.get_relevant_chunks(question)
for text, score in chunks:
    print(f"[{score:.4f}] {text}")

# Then get the actual answer
print("\nAnswer:", rag.invoke(question))
```

---

## Common pitfalls

**Testing RAG with facts the LLM might already know.**
If you test retrieval using real, well-known facts ("capital of France"),
you can't actually tell whether a correct answer came from your retrieved
context or from the model's own training data — the demo might *look*
successful even if retrieval is silently broken. Testing with fictional,
made-up facts (like a fake company) is the reliable way to prove
retrieval is genuinely driving the answer — if the LLM gets it right, it
had no other way to know.

**Forgetting the grounding instruction in the prompt.**
Without an explicit instruction like *"If the answer isn't in the
context, say you don't know,"* a model will often fill gaps with
plausible-sounding guesses instead of admitting uncertainty — a classic
hallucination risk. This instruction is doing real, necessary work, not
just sitting there as a suggestion; test it deliberately with a question
your knowledge base can't answer.

**Wrong prompt variable names.**
`RAGChain` doesn't validate that your wrapped chain's `PromptTemplate` has
`context` and `question` as its variables — that's documented as a
contract, not enforced at construction. If your template uses different
variable names, you'll get a clear error from `PromptTemplate.invoke()`
itself (missing variables), not from `RAGChain` directly.

**Retrieval quality is only as good as `k`.**
Too small a `k` might miss relevant context; too large might dilute the
prompt with irrelevant chunks, or exceed context limits with a large
knowledge base. `k=3` is a reasonable starting default, not a universal
answer — tune it based on your actual data.

---

## Where this is used next

RAG is the second-to-last layer — retrieval plus generation, working
together as a single `Runnable`. The final doc, `16_agents.md`, covers
the capstone: an LLM that can take *multiple* steps, choosing which tools
to call (including, potentially, this exact `RAGChain` wrapped as a
tool) — looping until it reaches a final answer.
```
