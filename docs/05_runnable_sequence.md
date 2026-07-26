# RunnableSequence

Runs multiple `Runnable` objects one after another, feeding each step's
output into the next step's input.

---

## What it is

`RunnableSequence` is what actually gets built when you write:

```python
chain = prompt | model | parser
```

The `|` operator (defined on `Runnable`, see `01_runnable.md`) doesn't do
the chaining itself — it just constructs a `RunnableSequence` out of
whatever's on either side of it.

```python
dict
 │
 ▼
PromptTemplate
 │
 ▼
string
 │
 ▼
ChatModel
 │
 ▼
AIMessage
 │
 ▼
OutputParser
 │
 ▼
string
```

---

## Why it exists

Without it, chaining components would mean writing this by hand every
time:

```python
result = parser.invoke(
    model.invoke(
        prompt.invoke(data)
    )
)
```

That nests worse with every additional step, and it's error-prone to
reorder. `RunnableSequence` turns any number of steps into one flat,
readable pipeline, and gives you `verbose`/callback support,
streaming, and async execution across the whole chain for free.

---

## Basic usage

```python
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import StringOutputParser

prompt = PromptTemplate(
    template="Explain {topic} in one sentence.",
    input_variables=["topic"],
)
model = ChatModel()
parser = StringOutputParser()

chain = prompt | model | parser   # builds a RunnableSequence

result = chain.invoke({"topic": "gravity"})
print(result)
```

You can also construct it directly, without `|`, if you prefer:

```python
from educhain.core.sequence import RunnableSequence

chain = RunnableSequence(prompt, model, parser)
```

---

## API Reference

### `RunnableSequence(*steps, verbose=False, callbacks=None)`

| Parameter | Type | Description |
|---|---|---|
| `*steps` | two or more `Runnable` objects | The pipeline, in execution order |
| `verbose` | `bool` | If `True` and no `callbacks` given, attaches a built-in `PrintCallbackHandler` automatically |
| `callbacks` | `list[CallbackHandler]`, optional | Custom observability hooks — see `12_callbacks.md` |

**Raises at construction:**
- `ValueError` — if fewer than 2 steps are given
- `TypeError` — if any step isn't a `Runnable`

### `.invoke(input_data)`

Runs every step in order, passing each step's output as the next step's
input. Fires callback hooks around each step (`on_step_start`,
`on_step_end`, `on_error`) if any are attached.

**Returns:** whatever the final step returns.

### `.stream(input_data)`

Runs every step normally *except* the last streaming-capable step, which
streams chunk by chunk. See `10_streaming.md` for exactly how the
source/transformer split works.

### `.ainvoke(input_data)`

Awaits every step in order using `ainvoke()`. See `11_async_execution.md`.

### `__or__(other)`

Chaining another `Runnable` (or another `RunnableSequence`) onto an
existing sequence **flattens** rather than nests:

```python
chain1 = prompt | model
chain2 = chain1 | parser
# chain2.steps == (prompt, model, parser) — flat, not nested
```

---

## Full example — with callbacks

```python
from educhain.core.sequence import RunnableSequence
from educhain.core.callbacks import PrintCallbackHandler
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import StringOutputParser

prompt = PromptTemplate(
    template="Give one fact about {topic}.",
    input_variables=["topic"],
)

chain = RunnableSequence(
    prompt, ChatModel(), StringOutputParser(),
    callbacks=[PrintCallbackHandler()],
)

result = chain.invoke({"topic": "black holes"})
```

This prints a step-by-step trace (`[Running] PromptTemplate...`,
`[Done] PromptTemplate ✔`, and so on) without any of that logic living
inside `RunnableSequence` itself — see `12_callbacks.md` for why that
separation matters.

---

## Common pitfalls

**Fewer than 2 steps.**
```python
RunnableSequence(ChatModel())
# ValueError: RunnableSequence requires at least two runnables.
```
A "sequence" of one step isn't really a sequence — just call `.invoke()`
on that one `Runnable` directly.

**A non-`Runnable` step.**
```python
RunnableSequence(prompt, "not a runnable")
# TypeError: not a runnable is not a Runnable. Every step in the chain must implement invoke().
```
This is validated at construction time, not when you call `.invoke()` —
so a broken chain fails immediately and obviously, not deep inside a
confusing stack trace later.

**Expecting `verbose=True` to give fine control.**
`verbose=True` is a convenience shortcut — it silently attaches a
`PrintCallbackHandler` for you. If you want custom logging behavior
(timing, counting, sending to a dashboard), pass your own handler via
`callbacks=[...]` instead. See `12_callbacks.md`.

**Assuming `.stream()` streams every step.**
Only the step that can genuinely produce chunks (usually `ChatModel`)
actually streams. Steps before it run normally with `.invoke()`, since
there's nothing to "chunk" about formatting a prompt string. This is
covered in full in `10_streaming.md` — including a real bug that was hit
and fixed while building this exact mechanism.

---

## Where this is used next

`RunnableSequence` is the backbone of nearly every example in this
documentation. The next doc, `06_runnable_parallel.md`, covers what
happens when you want multiple chains to run on the *same* input at the
same time, instead of one after another.