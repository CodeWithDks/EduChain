# EduChain Documentation

Complete reference for every component in EduChain, in the order they
were built. Read start to finish to learn EduChain the way it was
actually built — dependency by dependency — or jump straight to whatever
you need.

> New here? Start with [`00_overview.md`](./00_overview.md) — it explains
> the core idea (`Runnable`) and how the rest of this documentation is
> organized.

---

## Layer 1 — Core Primitives

The foundation everything else is built on: format a prompt, call a
model, parse the output, and compose it all together.

| Doc | Covers |
|---|---|
| [`01_runnable.md`](./01_runnable.md) | The base abstraction — one shared interface (`invoke`, `stream`, `ainvoke`) that every component implements |
| [`02_prompt_template.md`](./02_prompt_template.md) | Turning a dictionary into a formatted prompt string |
| [`03_chat_model.md`](./03_chat_model.md) | Wrapping an LLM — sending prompts, getting `AIMessage` back |
| [`04_output_parsers.md`](./04_output_parsers.md) | Converting raw model output into clean strings or JSON |
| [`05_runnable_sequence.md`](./05_runnable_sequence.md) | Chaining steps together with `|` — the mechanism behind `prompt | model | parser` |
| [`06_runnable_parallel.md`](./06_runnable_parallel.md) | Running multiple branches on the same input at once |
| [`07_runnable_passthrough.md`](./07_runnable_passthrough.md) | Keeping the original input alongside processed results |
| [`08_runnable_lambda.md`](./08_runnable_lambda.md) | Dropping any plain Python function into a chain |

---

## Layer 2 — Execution Models

Different ways to *run* the primitives above: with memory, streamed,
asynchronously, or with pluggable observability.

| Doc | Covers |
|---|---|
| [`09_memory.md`](./09_memory.md) | Remembering conversation turns across multiple calls |
| [`10_streaming.md`](./10_streaming.md) | Getting responses token by token, and how source/transformer detection works |
| [`11_async_execution.md`](./11_async_execution.md) | Running chains with `async`/`await` for real concurrency |
| [`12_callbacks.md`](./12_callbacks.md) | Pluggable hooks for observing what's happening inside a chain |

---

## Layer 3 — Agentic Capabilities

The most advanced layer — letting an LLM decide to act, retrieve real
information, and reason across multiple steps.

| Doc | Covers |
|---|---|
| [`13_tool_calling.md`](./13_tool_calling.md) | Letting an LLM call Python functions it chooses on its own |
| [`14_vector_store.md`](./14_vector_store.md) | Storing text and searching it by meaning, with hand-written cosine similarity |
| [`15_rag.md`](./15_rag.md) | Answering questions using retrieved context instead of guessing |
| [`16_agents.md`](./16_agents.md) | The capstone — a full reasoning loop combining tools, callbacks, and RAG |

---

## Quick links

- **Project root:** [`../README.md`](../README.md) — installation, quick start, project structure
- **Build history & design decisions:** [`../ROADMAP.md`](../ROADMAP.md) — what was built, in what order, and why
- **Working examples:** `demo_*.py` files in the project root — each doc above has a matching runnable demo
- **Test suite:** `test_all_features.py` — 36 tests covering every component documented here

---

## How these docs are organized

Every doc in this set follows the same structure:

1. **What it is** — a plain description
2. **Why it exists** — the actual problem it solves
3. **Basic usage** — the smallest working example
4. **API reference** — parameters, methods, return types
5. **Full example** — a more realistic use case
6. **Common pitfalls** — real issues hit while building EduChain, documented honestly, not hypothetically

This isn't accidental — EduChain was built in dependency order (see the
three layers above), and each doc assumes you understand what came before
it in that order, while still being usable on its own if you already
know the basics.