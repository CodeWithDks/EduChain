# EduChain — Development Roadmap

**Author:** Deepak Singh (github.com/CodeWithDks)
**Project:** EduChain — a mini LangChain clone, built for learning

This file tracks what's built, what's tested, and what's coming next —
so every session starts with focus instead of re-deciding priorities.

---

## ✅ Completed & Verified (20/20 tests passing)

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
- `ChatMessageHistory` — remembers conversation turns across multiple `.invoke()` calls

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

### Test Coverage
- `test_all_features.py` — 20 tests, covers happy paths + validation errors
  for every primitive above
- `demo_all_features.py` — real usage demo, all features working together
- `demo_async.py` — async chains + speed comparison
- `demo_callbacks.py` — built-in + custom handlers, multi-handler, error hooks

---

## 🚧 In Progress / Next Up

### 1. Tool Calling — *next session*
- `educhain/core/tool.py` — `Tool` class wrapping a plain Python function
  (auto-generate schema from type hints + docstring, no hand-written JSON schema)
- `ChatModel` gains `tools=[...]` support via `.bind_tools()`
- Detect tool-call responses vs. plain text responses
- Execute the chosen tool, feed result back into the conversation

### 2. Vector Stores
- Basic in-memory store: list of embeddings + cosine similarity search
- Understand the mechanism before reaching for FAISS/Chroma

### 3. RAG (Retrieval-Augmented Generation)
- Combine Vector Store retrieval + existing `PromptTemplate` + chain
- Realization goal: RAG isn't a new primitive, it's a *pattern* built from
  what we already have

### 4. Agents
- The capstone — built entirely from Tool Calling + Callbacks + a loop
- LLM decides action → action executes → result feeds back → repeat until done
- This is *why* Tool Calling and Callbacks had to come before this

---

## 📌 Known Cleanup Items (not blocking, but don't forget)

- [ ] Check if `educhain/core/history.py` is a leftover duplicate of
      `educhain/memory/chat_history.py` — confirm and remove if unused
- [ ] `ChatModel` doesn't currently accept `callbacks=[...]` — decide if this
      is worth adding for error visibility at the model level, or if
      sequence-level callbacks are enough
- [ ] Consider adding `ainvoke()` to `RunnableLambda` and `RunnablePassthrough`
      explicitly, instead of relying on the base class fallback

---

## Guiding Principle

Every feature gets built in **dependency order**, not "coolest first."
Async → Callbacks → Tool Calling → Vector Stores → RAG → Agents.
Each one is genuinely needed by the next — skipping ahead means rebuilding
things twice. This order is deliberate, not arbitrary.

---

*Last updated: after completing Callback System, all 20 tests passing.*