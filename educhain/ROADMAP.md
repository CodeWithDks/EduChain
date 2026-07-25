# EduChain — Development Roadmap

**Author:** Deepak Singh (github.com/CodeWithDks)
**Project:** EduChain — a mini LangChain clone, built for learning

This file tracks what's built, what's tested, and what's coming next —
so every session starts with focus instead of re-deciding priorities.

---

## ✅ Completed & Verified (26/26 tests passing)

### Core Primitives
- `Runnable` — base class, every component implements `.invoke()`
- `PromptTemplate` — dict → formatted prompt string
- `ChatModel` — wraps any LangChain chat model, defaults to `ChatOpenAI()`
- `StringOutputParser` — AIMessage → plain string
- `JsonOutputParser` — AIMessage → Python dict
- `RunnableSequence` — chains steps together via `|` operator, auto-flattens nested sequences
- `RunnableParallel` — runs multiple branches on the same input (thread-based)
- `RunnablePassthrough` — returns input unchanged (useful inside RunnableParallel)
- `RunnableLambda` — wraps any plain Python function as a chain step

### Memory
- `MessageHistory` (`core/history.py`) — raw message store (list + add/clear)
- `ChatMessageHistory` (`memory/chat_history.py`) — wraps a chain, auto-injects
  history into prompts, auto-saves turns

### Streaming
- `ChatModel.stream()` — token-by-token output from the LLM
- `RunnableSequence.stream()` — smart source/transformer detection via `IS_STREAM_TRANSFORMER`
  flag, so streaming works correctly through `prompt | model | parser`

### Async Execution
- `Runnable.ainvoke()` — default fallback on base class
- `ChatModel.ainvoke()` — real async LLM calls
- `RunnableSequence.ainvoke()` — awaits each step in order
- `RunnableParallel.ainvoke()` — true concurrency via `asyncio.gather()`
  (vs. thread-based `invoke()`)

### Callback System
- `CallbackHandler` — base class, hooks: `on_chain_start`, `on_step_start`,
  `on_step_end`, `on_error`, `on_chain_end`
- `PrintCallbackHandler` — built-in handler, replaces old hardcoded `verbose` prints
- `RunnableSequence` fires callbacks around every step
- Custom handlers proven working (e.g. step timing/counting) with zero changes
  to core chain code

### Tool Calling
- `educhain/core/tool.py` — `Tool` class, auto-generates JSON schema from
  function type hints + docstring (no hand-written schemas required)
- `ChatModel` accepts `tools=[...]`, binds via `.bind_tools(schemas, tool_choice="auto")`
- `ChatModel.has_tool_calls()` — detects tool-call vs. plain-text responses
- `ChatModel.run_tool_calls()` — executes the LLM's chosen tool(s), returns
  structured results
- Known limitation: `ChatModel.invoke()` only accepts single string prompts,
  not full message-list conversations — full tool round-trips currently
  require reaching into the raw underlying model directly (see demo_tools.py
  demo 4). **Deferred on purpose — this is genuinely an Agent-phase problem,
  to be solved when Agents give it a concrete use case, not speculatively now.**

### Vector Stores
- `educhain/core/vectorstore.py` — `InMemoryVectorStore` class
- Uses `OpenAIEmbeddings` for text → vector conversion (not reimplemented —
  same reasoning as using LangChain's `.bind_tools()` for Tool Calling)
- Hand-written cosine similarity search (the actual "search" mechanism —
  this part IS built from scratch, on purpose)
- `add_texts()` — batch-embeds and stores text chunks
- `similarity_search(query, k=3)` — returns top-k most relevant chunks with scores
- Verified: correctly retrieves semantically relevant text even when the query
  shares no exact keywords with the source text (proven in demo_vectorstore.py
  demo 2 — "What framework is Deepak building?" correctly surfaced EduChain-
  related facts over a more keyword-obvious "Python" fact)

  ### RAG (Retrieval-Augmented Generation)
- `educhain/core/rag.py` — `RAGChain` class, inherits from `Runnable`
- Wraps a vector store + an existing chain (`prompt | model | parser`)
- `invoke(question)` — retrieves relevant chunks, injects as `context`,
  runs the wrapped chain
- `get_relevant_chunks(question)` — inspect retrieval separately from generation
- Duck-typed vector store check (`hasattr(vectorstore, "similarity_search")`)
  instead of `isinstance`, so any compatible store works, not just
  `InMemoryVectorStore` specifically
- Verified with fictional data (a made-up company) specifically so correct
  answers are undeniable proof of retrieval working — not coincidence from
  the LLM's own training knowledge
- Confirmed: correctly declines to answer when the information isn't in
  the retrieved context, instead of hallucinating
- Key realization confirmed in practice: RAG is not a new primitive, it's
  a *pattern* assembled entirely from existing pieces (VectorStore +
  PromptTemplate + RunnableSequence)

### Test Coverage
-## ✅ Completed & Verified (30/30 tests passing)
  for every primitive above
- `demo_all_features.py` — real usage demo, all features working together
- `demo_async.py` — async chains + speed comparison
- `demo_callbacks.py` — built-in + custom handlers, multi-handler, error hooks
- `demo_tools.py` — tool detection, execution, multi-tool selection, full
  round-trip, validation
- `demo_vectorstore.py` — semantic search across mixed topics, validation

---

## 🚧 In Progress / Next Up

### Agents — the final roadmap item
- The capstone — built entirely from Tool Calling + Callbacks + a loop
- LLM decides action → action executes → result feeds back → repeat until done
- **Must solve first:** `ChatModel.invoke()` currently only accepts single
  string prompts, not full message-list conversations. This was deliberately
  deferred from the Tool Calling phase — Agents is where this gap becomes
  unavoidable to fix, since an agent loop IS repeated multi-message
  tool round-trips.
- Once built, RAG can be wrapped as a Tool — giving the Agent a genuinely
  useful capability (search a real knowledge base) instead of only
  toy demo functions like weather or addition
## 📌 Known Cleanup Items

- [x] ~~Check if `core/history.py` duplicates `memory/chat_history.py`~~ —
      **Resolved: not a duplicate.** Correct separation — `core/history.py`
      is the raw data store, `memory/chat_history.py` is the chain-integration
      wrapper that depends on it. Keep both as-is.
- [ ] `ChatModel` doesn't currently accept `callbacks=[...]` — decide if this
      is worth adding for error visibility at the model level, or if
      sequence-level callbacks are enough
- [ ] Consider adding `ainvoke()` to `RunnableLambda` and `RunnablePassthrough`
      explicitly, instead of relying on the base class fallback
- [ ] `ChatModel.invoke()` message-list support — deferred to Agent phase
      (see Tool Calling section above)

---

## Guiding Principle

Every feature gets built in **dependency order**, not "coolest first."
Async → Callbacks → Tool Calling → Vector Stores → RAG → Agents.
Each one is genuinely needed by the next — skipping ahead means rebuilding
things twice. This order is deliberate, not arbitrary.

---

*Last updated: after completing Vector Stores, all 26 tests passing.*