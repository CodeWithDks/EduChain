# EduChain — Overview

EduChain is a mini LangChain clone, built from scratch to understand how
modern LLM frameworks are actually engineered — not just how to call their
APIs.

Every piece in this documentation was built in a deliberate order, where
each new feature depended on the ones before it. That order is preserved
in these docs, so reading them in sequence teaches EduChain the same way
it was built.

---

## Why EduChain exists

Most people learn LangChain by importing it and calling `.invoke()`.
That teaches you the API surface, but not *why* it's shaped the way it is —
why every component shares one interface, why streaming needs special
handling, why tool calling and agents are built on the same primitives as
a basic prompt chain.

EduChain answers those questions by rebuilding the mechanisms by hand:
cosine similarity search, the streaming source/transformer detection,
the callback dispatch system, the agent reasoning loop — all written from
scratch, not imported.

> EduChain is an educational project. It is not intended to replace
> LangChain or be feature-compatible with it.

---

## The core idea: one interface, everywhere

Every component in EduChain inherits from a single base class — `Runnable`
— and implements the same interface:

```python
invoke(input)      # run it synchronously
stream(input)       # run it and get output in chunks
ainvoke(input)       # run it asynchronously
```

Because every component — a prompt template, a chat model, a parser, an
entire multi-step agent — honors this same interface, they can all be
composed together the same way, using the same operator:

```python
chain = prompt | model | parser
```

This one design decision is what makes everything else in EduChain
possible. A `RunnableSequence` doesn't need to know whether a step is a
prompt formatter or a full agent — it just calls `.invoke()` on it and
trusts the result.

---

## Architecture

```
                                  Runnable
                                     │
        ┌───────────┬───────────┬───┴───────┬───────────┬──────────┐
        ▼           ▼           ▼           ▼           ▼          ▼
 PromptTemplate  ChatModel  OutputParser  Passthrough   Lambda    Agent
                     │                                              │
                     ▼                                              ▼
              (tools bound)                                  ChatModel + Tools
                     │                                          + Callbacks
                     ▼                                              │
              RunnableSequence ◄──── RAGChain ◄──── InMemoryVectorStore
                     │
                     ▼
              RunnableParallel
                     │
                     ▼
              Memory & Chat History
```

Everything below `Runnable` is a specialization of the same idea: take an
input, produce an output, be composable with everything else.

---

## How EduChain was built (and how to read these docs)

EduChain wasn't built feature-by-feature in random order. It was built in
**dependency order** — each layer only started once the layer below it was
solid and tested. These docs follow that same order:

### Layer 1 — Core Primitives
The foundation. A prompt formatter, a model wrapper, an output parser, and
the composition tools (`RunnableSequence`, `RunnableParallel`,
`RunnablePassthrough`, `RunnableLambda`) that let you wire them together.

→ `01_runnable.md` through `08_runnable_lambda.md`

### Layer 2 — Execution Models
Once the primitives worked, EduChain gained new *ways* to run them: with
memory across turns, streamed token-by-token, run asynchronously, and with
pluggable observability via callbacks.

→ `09_memory.md` through `12_callbacks.md`

### Layer 3 — Agentic Capabilities
The most advanced layer, and the one every earlier layer exists to support.
Tool Calling lets an LLM choose to act. Vector Stores and RAG let it answer
using real retrieved knowledge instead of guessing. Agents combine all of
it into a genuine reasoning loop — ask, decide, act, observe, repeat.

→ `13_tool_calling.md` through `16_agents.md`

---

## Reading this documentation

Each doc in this set follows the same shape:

1. **What it is** — a plain description, no jargon
2. **Why it exists** — the actual problem it solves
3. **Basic usage** — the smallest working example
4. **API reference** — constructor parameters, methods, return types
5. **Full example** — a more realistic use case
6. **Common pitfalls** — real issues hit while building EduChain, and how
   they were actually fixed (not hypothetical — these are documented bugs
   from real test runs)

You can read start to finish to learn EduChain the way it was built, or
jump directly to any single doc — each one is written to stand on its own.

---

## Where to go next

- New to EduChain? Start with `01_runnable.md`.
- Just want to use a specific piece? Jump straight to its doc — the numbers
  in the filenames tell you where it sits in the dependency chain, not that
  you're required to read everything before it.
- Want the full build history, including test results and design decisions
  made along the way? See `ROADMAP.md` in the project root.
```