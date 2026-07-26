# Callbacks

Pluggable hooks that let you observe what's happening inside a chain —
without hardcoding logging logic into the chain itself.

---

## What it is

`CallbackHandler` is a base class with hook methods that fire at specific
moments during a chain's execution: before a step runs, after it
completes, and if it fails. By default, every hook does nothing — you
subclass it and override only the hooks you actually care about:

```python
class MyLogger(CallbackHandler):
    def on_step_start(self, step_name, input_data):
        print(f"Starting {step_name}")

chain = RunnableSequence(prompt, model, parser, callbacks=[MyLogger()])
```

EduChain also ships a ready-made handler, `PrintCallbackHandler`, which
prints a clean step-by-step trace — this replaced what used to be
hardcoded `print()` statements directly inside `RunnableSequence`.

---

## Why it exists

Before callbacks existed, the only way to see what a chain was doing was
a `verbose=True` flag that printed hardcoded messages baked directly into
`RunnableSequence`. That worked, but it meant:

- You could only ever get exactly the output that was hardcoded — no way
  to log to a file, send to a monitoring dashboard, or count anything
  custom.
- Adding new observability behavior meant editing `RunnableSequence`
  itself, every time.

The callback system fixes this with the **Observer pattern**: define hook
points, let anyone plug in behavior at those points, and the core chain
code never needs to know what's actually watching it.

```python
class StepCounterHandler(CallbackHandler):
    def __init__(self):
        self.step_count = 0

    def on_step_end(self, step_name, output_data):
        self.step_count += 1
```

This works with **zero changes** to `RunnableSequence` — that's the whole
point.

---

## Basic usage

```python
from educhain.core.sequence import RunnableSequence
from educhain.core.callbacks import PrintCallbackHandler
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import StringOutputParser

prompt = PromptTemplate(template="Answer: {question}", input_variables=["question"])

chain = RunnableSequence(
    prompt, ChatModel(), StringOutputParser(),
    callbacks=[PrintCallbackHandler()],
)

result = chain.invoke({"question": "What is the tallest mountain?"})
```

This prints a full trace: a start banner, `[Running]`/`[Done]` for each
step, and a finish banner — all without any of that logic living inside
`RunnableSequence`.

---

## API Reference

### `CallbackHandler` (base class)

| Hook | Fires when |
|---|---|
| `on_chain_start(chain_name, input_data)` | Once, before the first step runs |
| `on_step_start(step_name, input_data)` | Before each individual step |
| `on_step_end(step_name, output_data)` | After each individual step completes |
| `on_error(step_name, error)` | If a step raises an exception |
| `on_chain_end(chain_name, output_data)` | Once, after the last step finishes |

Every hook does nothing by default — override only what you need.

### `PrintCallbackHandler` (built-in)

A ready-to-use handler implementing all five hooks to print a clean
console trace. Used automatically when `RunnableSequence(..., verbose=True)`
is set without explicit `callbacks`.

### Attaching callbacks

| Component | Parameter |
|---|---|
| `RunnableSequence(*steps, callbacks=[...])` | Construction-time |
| `ChatModel(callbacks=[...])` | Construction-time — fires `on_error` if the underlying model call fails |
| `Agent(model, callbacks=[...])` | Construction-time — fires around each reasoning iteration |

You can pass multiple handlers at once — all of them fire, in the order
given.

---

## Full example — a custom handler

```python
import time
from educhain.core.sequence import RunnableSequence
from educhain.core.callbacks import CallbackHandler
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import StringOutputParser

class StepTimer(CallbackHandler):
    """Tracks how long each step takes, without touching RunnableSequence."""

    def __init__(self):
        self.timings = {}
        self._start = None

    def on_step_start(self, step_name, input_data):
        self._start = time.perf_counter()

    def on_step_end(self, step_name, output_data):
        self.timings[step_name] = time.perf_counter() - self._start

    def on_chain_end(self, chain_name, output_data):
        for name, seconds in self.timings.items():
            print(f"{name}: {seconds:.3f}s")


prompt = PromptTemplate(template="Give one fact about {topic}.", input_variables=["topic"])
timer = StepTimer()

chain = RunnableSequence(prompt, ChatModel(), StringOutputParser(), callbacks=[timer])
result = chain.invoke({"topic": "black holes"})

# Output shows exactly which step was the bottleneck —
# almost always the ChatModel call, not the prompt formatting or parsing
```

---

## Common pitfalls

**Expecting `on_error` to stop the exception from propagating.**
`on_error` is a *notification*, not a way to swallow errors. The original
exception still raises after every handler's `on_error` fires — this is
intentional. Callbacks are for observing failures, not silently absorbing
them; that would hide real bugs.

**Registering a handler but overriding no hooks.**
```python
class DoNothing(CallbackHandler):
    pass  # inherits every hook as a no-op

chain = RunnableSequence(prompt, model, parser, callbacks=[DoNothing()])
```
This is completely valid, just pointless — nothing will fire. Only
override the specific hooks you actually need.

**Confusing `verbose=True` with a real handler.**
`verbose=True` is a convenience shortcut that only works if you *don't*
pass `callbacks` explicitly — under the hood it just attaches
`PrintCallbackHandler` for you. If you pass both `verbose=True` and your
own `callbacks=[...]`, your explicit callbacks take priority and
`verbose` is effectively ignored. Prefer being explicit with `callbacks=`
once you need more than basic print output.

---

## Where this is used next

Callbacks close out the execution-model layer — Memory, Streaming, Async,
and now observability. The next doc, `13_tool_calling.md`, moves into
EduChain's most advanced layer: letting an LLM decide to *act*, not just
respond with text.