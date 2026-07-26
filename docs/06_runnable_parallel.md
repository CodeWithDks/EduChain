# RunnableParallel

Runs multiple `Runnable` branches on the same input at the same time,
returning a dictionary of all their results.

---

## What it is

Where `RunnableSequence` runs steps one after another, `RunnableParallel`
runs several independent chains side by side, on the exact same input:

```
Input
  │
  ├────────► Summary Chain
  │
  ├────────► Joke Chain
  │
  └────────► Fact Chain

Returns:

{
    "summary": "...",
    "joke": "...",
    "fact": "..."
}
```

Each branch is a completely independent `Runnable` — often a whole
`prompt | model | parser` chain of its own.

---

## Why it exists

If you need three different responses to the same input — a summary, a
joke, and a fact about the same topic, say — running them one after
another with `RunnableSequence` wastes time: each LLM call waits for the
previous one to finish even though they don't depend on each other at all.
`RunnableParallel` runs them concurrently instead, so the total time is
closer to the *slowest* single branch, not the *sum* of all of them.

---

## Basic usage

```python
from educhain.core.parallel import RunnableParallel
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import StringOutputParser

model = ChatModel()
parser = StringOutputParser()

summary_chain = (
    PromptTemplate(template="Summarize in one sentence: {text}", input_variables=["text"])
    | model | parser
)

joke_chain = (
    PromptTemplate(template="Tell a one-line joke about: {text}", input_variables=["text"])
    | model | parser
)

parallel = RunnableParallel(summary=summary_chain, joke=joke_chain)

result = parallel.invoke({"text": "robots"})
print(result["summary"])
print(result["joke"])
```

The keyword argument names (`summary=`, `joke=`) become the dictionary
keys in the result — there's no fixed schema, you name your own branches.

---

## API Reference

### `RunnableParallel(**runnables)`

| Parameter | Type | Description |
|---|---|---|
| `**runnables` | keyword args, each a `Runnable` | Each keyword becomes a key in the result dict; each value is the branch that runs to produce it |

**Raises at construction:**
- `ValueError` — if zero runnables are given
- `TypeError` — if any branch isn't a `Runnable`

### `.invoke(input_data)`

Runs every branch on the same `input_data`, concurrently, using
`ThreadPoolExecutor`.

**Returns:** `dict` — keys match the constructor's keyword names, values
are each branch's result

### `.ainvoke(input_data)`

Same behavior, but uses `asyncio.gather()` for true async concurrency
instead of threads. See `11_async_execution.md` for when this actually
matters (short answer: at larger scale, not for 2-3 branches).

---

## Full example — with RunnablePassthrough

A common pattern: keep the original input alongside a processed result.

```python
from educhain.core.parallel import RunnableParallel
from educhain.core.passthrough import RunnablePassthrough
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import StringOutputParser

translate_chain = (
    PromptTemplate(template="Translate to Hindi: {text}", input_variables=["text"])
    | ChatModel() | StringOutputParser()
)

parallel = RunnableParallel(
    original=RunnablePassthrough(),
    translated=translate_chain,
)

result = parallel.invoke({"text": "Good morning"})
print(result["original"])     # {'text': 'Good morning'}
print(result["translated"])   # "सुप्रभात"
```

See `07_runnable_passthrough.md` for more on this pattern.

---

## Common pitfalls

**Zero branches.**
```python
RunnableParallel()
# ValueError: At least one runnable is required.
```

**A non-`Runnable` branch.**
```python
RunnableParallel(good=some_chain, bad="not a runnable")
# TypeError: 'bad' is not a Runnable. Every branch passed to RunnableParallel must implement invoke().
```
Note the error names the specific bad key (`'bad'`), not just the value —
makes it immediately obvious which branch is the problem when you have
several.

**Expecting `invoke()` and `ainvoke()` to have identical speed.**
For a small number of branches (2-4), thread-based `invoke()` and
async-based `ainvoke()` will often be roughly the same speed — both
achieve real concurrency for network-bound work like LLM calls. The
difference shows up at larger scale: threads have real OS overhead per
thread, while `asyncio` handles many more concurrent operations on a
single thread more cheaply. Don't expect a dramatic speed difference with
just a couple of branches.

---

## Where this is used next

`RunnableParallel` is the building block behind fan-out patterns — asking
several independent questions about the same input at once. The next doc,
`07_runnable_passthrough.md`, covers its frequent companion: a way to keep
the original input available alongside whatever the parallel branches
produce.
```
