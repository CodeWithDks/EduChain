# Async Execution

Run chains using Python's `async`/`await`, so slow LLM calls don't block
everything else your program is doing.

---

## What it is

Every `Runnable` supports an async counterpart to `.invoke()`:

```python
result = await chain.ainvoke({"topic": "gravity"})
```

Same inputs, same outputs, same validation — the only difference is *how*
it runs. `.invoke()` blocks until the LLM responds. `.ainvoke()` lets
other work happen while waiting on the network.

---

## Why it exists

In a script that only ever does one thing at a time, `.invoke()` is
perfectly fine. But in a real application — a web server handling many
users at once, or a program running several independent chains together —
blocking on one slow network call while everything else waits is wasteful.
`ainvoke()` lets you run many chains concurrently without needing threads
for each one.

### Where the base class fallback comes from

Not every component benefits from real async — `PromptTemplate` formatting
a string has no network call to wait on. So the base `Runnable` class
(see `01_runnable.md`) defines a default:

```python
async def ainvoke(self, input_data):
    return self.invoke(input_data)   # just run invoke() normally
```

Only components doing actual I/O override this with something real:

- **`ChatModel.ainvoke()`** — awaits the underlying model's own
  `.ainvoke()`, a genuine async network call
- **`RunnableSequence.ainvoke()`** — awaits each step in order (not the
  fallback, since that would silently call sync `invoke()` on every step
  and defeat the point)
- **`RunnableParallel.ainvoke()`** — runs every branch **concurrently**
  using `asyncio.gather()`, instead of the thread-based approach
  `.invoke()` uses

---

## Basic usage

```python
import asyncio
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import StringOutputParser

async def main():
    prompt = PromptTemplate(
        template="Answer briefly: {question}",
        input_variables=["question"],
    )
    chain = prompt | ChatModel() | StringOutputParser()

    answer = await chain.ainvoke({"question": "What is the capital of Japan?"})
    print(answer)

asyncio.run(main())
```

---

## API Reference

### `Runnable.ainvoke(input_data)` (base class default)

Falls back to running `.invoke()` synchronously. Safe for components with
no real async work to do.

### `ChatModel.ainvoke(input_data)`

Same validation as `.invoke()`. Awaits the underlying model's async call.

### `RunnableSequence.ainvoke(input_data)`

Awaits each step's `.ainvoke()` in order.

### `RunnableParallel.ainvoke(input_data)`

Runs every branch concurrently via `asyncio.gather()`.

**Returns:** `dict` — same shape as `.invoke()`, just produced
concurrently through the event loop instead of threads.

---

## Full example — concurrent independent chains

```python
import asyncio
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import StringOutputParser

async def main():
    prompt = PromptTemplate(
        template="Name one famous landmark in {city}.",
        input_variables=["city"],
    )
    chain = prompt | ChatModel() | StringOutputParser()

    cities = ["Paris", "Tokyo", "Cairo"]

    results = await asyncio.gather(
        *[chain.ainvoke({"city": city}) for city in cities]
    )

    for city, result in zip(cities, results):
        print(f"{city}: {result}")

asyncio.run(main())
```

All three chains run concurrently — none of them wait for the others to
finish before starting.

---

## Common pitfalls

**Expecting `ainvoke()` to always be dramatically faster than `invoke()`.**
For I/O-bound work like LLM API calls, Python's threads already achieve
real concurrency — they release the GIL while waiting on network I/O. In
practice, timing `RunnableParallel.invoke()` against `.ainvoke()` with a
small number of branches (2-4) often shows *similar* total time. The real
advantage of async shows up at scale: handling many more concurrent
operations without the overhead of spinning up an OS thread for each one.
Don't expect a dramatic speed win with just a couple of branches — that's
not where async actually pays off.

**Forgetting `RunnableSequence` needs its own `ainvoke()`, not the base
fallback.**
If `RunnableSequence` only inherited the base class's `ainvoke()`, it
would call `self.invoke(input_data)` — running the *entire chain*
synchronously, defeating the purpose entirely. It has to override
`ainvoke()` explicitly to await each step, which is exactly what it does.

**Mixing sync and async code carelessly.**
`asyncio.run(main())` needs to wrap your entire async entry point — you
can't casually call `await chain.ainvoke(...)` from regular synchronous
code without an event loop already running. If you're building a normal
script (not a web server), wrap your logic in an `async def main():` and
run it with `asyncio.run(main())`, as shown above.

---

## Where this is used next

Async execution changes how a chain runs internally. The next doc,
`12_callbacks.md`, covers a different concern entirely — getting
visibility into *what's happening* inside a chain while it runs, without
hardcoding print statements everywhere.